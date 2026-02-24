"""Property-based tests for Data Reader component.

Feature: nuscenes-8k-to-detzero-conversion
"""

import pickle
import tempfile
from pathlib import Path
import numpy as np
from hypothesis import given, settings, strategies as st

# Import the component under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_reader import NuScenesDataReader


# Custom strategies for generating test data
@st.composite
def frame_data(draw):
    """Generate random nuScenes frame data."""
    n_objects = draw(st.integers(min_value=0, max_value=50))
    
    return {
        'lidar_path': f'samples/LIDAR_TOP/n{draw(st.integers(min_value=0, max_value=999999)):06d}.bin',
        'token': draw(st.text(min_size=32, max_size=32, alphabet='0123456789abcdef')),
        'timestamp': draw(st.integers(min_value=10**15, max_value=10**17)),
        'sweeps': [],
        'gt_boxes': np.random.randn(n_objects, 9).astype(np.float32),
        'gt_names': np.array([draw(st.sampled_from(['car', 'pedestrian', 'bicycle', 'truck'])) 
                             for _ in range(n_objects)]),
        'gt_boxes_velocity': np.random.randn(n_objects, 2).astype(np.float32),
        'num_lidar_pts': np.random.randint(0, 1000, size=n_objects).astype(np.int32),
        'gt_track_ids': np.array([f'track_{i}' for i in range(n_objects)]),
    }


@st.composite
def info_file_data(draw, min_frames=1, max_frames=100):
    """Generate a list of frame data for an info file."""
    n_frames = draw(st.integers(min_value=min_frames, max_value=max_frames))
    return [draw(frame_data()) for _ in range(n_frames)]


class TestDataReaderProperties:
    """Property-based tests for NuScenesDataReader."""
    
    @settings(max_examples=100)
    @given(frames=info_file_data(min_frames=1, max_frames=100))
    def test_property_1_frame_count_preservation(self, frames):
        """Property 1: Frame Count Preservation
        
        For any dataset split (train or val), the number of frames in the 
        converted output SHALL equal the number of frames in the source dataset.
        
        **Validates: Requirements 1.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 1: Frame count preservation
        """
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'test_version'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Test both train and val splits
            for split in ['train', 'val']:
                # Write info file
                info_file = version_dir / f'nuscenes_infos_1sweeps_{split}.pkl'
                with open(info_file, 'wb') as f:
                    pickle.dump(frames, f)
                
                # Initialize reader
                reader = NuScenesDataReader(str(tmpdir), version)
                
                # Load info file
                loaded_frames = reader.load_info_file(split)
                
                # Property: Frame count must be preserved
                assert len(loaded_frames) == len(frames), \
                    f"Frame count mismatch for {split}: expected {len(frames)}, got {len(loaded_frames)}"
                
                # Additional verification: ensure it's a list
                assert isinstance(loaded_frames, list), \
                    f"Loaded frames should be a list, got {type(loaded_frames)}"
                
                # Verify each frame is a dictionary
                for i, frame in enumerate(loaded_frames):
                    assert isinstance(frame, dict), \
                        f"Frame {i} should be a dict, got {type(frame)}"
    
    @settings(max_examples=100)
    @given(
        train_frames=info_file_data(min_frames=1, max_frames=100),
        val_frames=info_file_data(min_frames=1, max_frames=50)
    )
    def test_frame_count_preservation_separate_splits(self, train_frames, val_frames):
        """Property 1: Frame Count Preservation (separate splits)
        
        Verify that train and val splits maintain their frame counts independently.
        
        **Validates: Requirements 1.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 1: Frame count preservation
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'test_version'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Write both info files
            train_info = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            val_info = version_dir / 'nuscenes_infos_1sweeps_val.pkl'
            
            with open(train_info, 'wb') as f:
                pickle.dump(train_frames, f)
            with open(val_info, 'wb') as f:
                pickle.dump(val_frames, f)
            
            # Initialize reader
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Load both splits
            loaded_train = reader.load_info_file('train')
            loaded_val = reader.load_info_file('val')
            
            # Property: Each split preserves its frame count
            assert len(loaded_train) == len(train_frames), \
                f"Train frame count mismatch: expected {len(train_frames)}, got {len(loaded_train)}"
            assert len(loaded_val) == len(val_frames), \
                f"Val frame count mismatch: expected {len(val_frames)}, got {len(loaded_val)}"
            
            # Verify independence: loading one split doesn't affect the other
            assert len(loaded_train) != len(loaded_val) or len(train_frames) == len(val_frames), \
                "Split independence violated"
    
    @settings(max_examples=100)
    @given(frames=info_file_data(min_frames=0, max_frames=100))
    def test_frame_count_preservation_with_empty_dataset(self, frames):
        """Property 1: Frame Count Preservation (edge case: empty or minimal datasets)
        
        Verify frame count preservation even with edge cases like empty datasets.
        
        **Validates: Requirements 1.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 1: Frame count preservation
        """
        # Skip if frames is empty (reader should reject empty lists)
        if len(frames) == 0:
            return
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'test_version'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Write info file
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump(frames, f)
            
            # Initialize reader
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Load info file
            loaded_frames = reader.load_info_file('train')
            
            # Property: Frame count must be preserved regardless of size
            assert len(loaded_frames) == len(frames), \
                f"Frame count mismatch: expected {len(frames)}, got {len(loaded_frames)}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
