"""Unit tests for NuScenesDataReader component.

Tests specific examples and edge cases for data loading functionality.
Validates: Requirements 1.2, 13.1
"""

import pickle
import tempfile
from pathlib import Path
import numpy as np
import pytest

# Import the component under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_reader import NuScenesDataReader


class TestNuScenesDataReaderInit:
    """Test initialization and setup."""
    
    def test_init_with_valid_path(self):
        """Test initialization with valid data path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = NuScenesDataReader(tmpdir, 'v1.0-test')
            assert reader.data_path == Path(tmpdir)
            assert reader.version == 'v1.0-test'
    
    def test_init_with_nonexistent_path(self):
        """Test initialization with non-existent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Data path not found"):
            NuScenesDataReader('/nonexistent/path', 'v1.0-test')


class TestLoadInfoFile:
    """Test loading info pickle files."""
    
    def test_load_valid_train_info_file(self):
        """Test loading valid training info file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create valid info file with sample data
            frames = [
                {
                    'lidar_path': 'samples/LIDAR_TOP/n000001.bin',
                    'token': 'abc123' * 5 + 'ab',  # 32 chars
                    'timestamp': 1234567890123456,
                    'gt_boxes': np.array([[1, 2, 3, 4, 5, 6, 0.5, 0.1, 0.2]], dtype=np.float32),
                    'gt_names': np.array(['car']),
                    'gt_boxes_velocity': np.array([[0.5, 0.3]], dtype=np.float32),
                    'num_lidar_pts': np.array([150], dtype=np.int32),
                    'gt_track_ids': np.array(['track_001']),
                },
                {
                    'lidar_path': 'samples/LIDAR_TOP/n000002.bin',
                    'token': 'def456' * 5 + 'de',
                    'timestamp': 1234567890223456,
                    'gt_boxes': np.array([[2, 3, 4, 5, 6, 7, 1.0, 0.2, 0.3]], dtype=np.float32),
                    'gt_names': np.array(['pedestrian']),
                    'gt_boxes_velocity': np.array([[0.1, 0.2]], dtype=np.float32),
                    'num_lidar_pts': np.array([80], dtype=np.int32),
                    'gt_track_ids': np.array(['track_002']),
                }
            ]
            
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump(frames, f)
            
            # Load and verify
            reader = NuScenesDataReader(str(tmpdir), version)
            loaded = reader.load_info_file('train')
            
            assert len(loaded) == 2
            assert loaded[0]['token'] == frames[0]['token']
            assert loaded[1]['token'] == frames[1]['token']
    
    def test_load_valid_val_info_file(self):
        """Test loading valid validation info file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create validation info file
            frames = [
                {
                    'lidar_path': 'samples/LIDAR_TOP/n000003.bin',
                    'token': 'val001' * 6 + 'va',
                    'timestamp': 1234567890323456,
                    'gt_boxes': np.array([[3, 4, 5, 6, 7, 8, 1.5, 0.3, 0.4]], dtype=np.float32),
                    'gt_names': np.array(['bicycle']),
                    'gt_boxes_velocity': np.array([[1.0, 0.5]], dtype=np.float32),
                    'num_lidar_pts': np.array([120], dtype=np.int32),
                    'gt_track_ids': np.array(['track_003']),
                }
            ]
            
            info_file = version_dir / 'nuscenes_infos_1sweeps_val.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump(frames, f)
            
            # Load and verify
            reader = NuScenesDataReader(str(tmpdir), version)
            loaded = reader.load_info_file('val')
            
            assert len(loaded) == 1
            assert loaded[0]['token'] == frames[0]['token']
    
    def test_load_missing_info_file(self):
        """Test handling missing info file - Validates Requirement 13.1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Should raise FileNotFoundError for missing file
            with pytest.raises(FileNotFoundError, match="Info file not found"):
                reader.load_info_file('train')
    
    def test_load_empty_info_file(self):
        """Test handling empty info file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create empty info file
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump([], f)
            
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Should raise ValueError for empty list
            with pytest.raises(ValueError, match="Invalid info file structure"):
                reader.load_info_file('train')
    
    def test_load_corrupted_info_file(self):
        """Test handling corrupted pickle file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create corrupted file
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                f.write(b'corrupted data')
            
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to load info file"):
                reader.load_info_file('train')
    
    def test_load_info_file_with_wrong_type(self):
        """Test handling info file with wrong data type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create info file with wrong type (dict instead of list)
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump({'wrong': 'type'}, f)
            
            reader = NuScenesDataReader(str(tmpdir), version)
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Invalid info file structure"):
                reader.load_info_file('train')


class TestLoadPointCloud:
    """Test loading point cloud files."""
    
    def test_load_valid_4_channel_point_cloud(self):
        """Test loading point cloud with 4 channels (x, y, z, intensity).
        
        Note: The implementation expects 5 channels. A 4-channel file will be
        reshaped incorrectly (e.g., 1000x4 becomes 800x5), which documents
        the actual behavior when wrong format is provided.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create 4-channel point cloud (4000 floats = 1000 points x 4 channels)
            points = np.random.randn(1000, 4).astype(np.float32)
            pc_file = tmpdir / 'test_4ch.bin'
            points.tofile(str(pc_file))
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            loaded = reader.load_point_cloud(str(pc_file))
            
            # 4000 floats reshaped to (-1, 5) becomes (800, 5)
            assert loaded.shape == (800, 5)
            assert loaded.dtype == np.float32
    
    def test_load_valid_5_channel_point_cloud(self):
        """Test loading point cloud with 5 channels (x, y, z, intensity, timestamp)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create 5-channel point cloud (standard nuScenes format)
            points = np.random.randn(1000, 5).astype(np.float32)
            pc_file = tmpdir / 'test_5ch.bin'
            points.tofile(str(pc_file))
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            loaded = reader.load_point_cloud(str(pc_file))
            
            assert loaded.shape == (1000, 5)
            assert loaded.dtype == np.float32
            np.testing.assert_array_almost_equal(loaded, points)
    
    def test_load_point_cloud_preserves_values(self):
        """Test that point cloud values are preserved exactly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create point cloud with specific values
            points = np.array([
                [1.5, 2.5, 3.5, 0.8, 1000.0],
                [-1.0, -2.0, -3.0, 0.5, 2000.0],
                [0.0, 0.0, 0.0, 1.0, 3000.0],
            ], dtype=np.float32)
            
            pc_file = tmpdir / 'test_values.bin'
            points.tofile(str(pc_file))
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            loaded = reader.load_point_cloud(str(pc_file))
            
            np.testing.assert_array_equal(loaded, points)
    
    def test_load_missing_point_cloud(self):
        """Test handling missing point cloud file - Validates Requirement 13.1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = NuScenesDataReader(tmpdir, 'v1.0-test')
            
            # Should raise FileNotFoundError
            with pytest.raises(FileNotFoundError, match="Point cloud file not found"):
                reader.load_point_cloud('/nonexistent/file.bin')
    
    def test_load_empty_point_cloud(self):
        """Test loading empty point cloud file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create empty file
            pc_file = tmpdir / 'empty.bin'
            pc_file.touch()
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            loaded = reader.load_point_cloud(str(pc_file))
            
            # Empty file should result in empty array
            assert loaded.shape == (0, 5)
    
    def test_load_point_cloud_with_large_dataset(self):
        """Test loading large point cloud (100k points)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create large point cloud
            points = np.random.randn(100000, 5).astype(np.float32)
            pc_file = tmpdir / 'large.bin'
            points.tofile(str(pc_file))
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            loaded = reader.load_point_cloud(str(pc_file))
            
            assert loaded.shape == (100000, 5)
            np.testing.assert_array_almost_equal(loaded, points)
    
    def test_load_point_cloud_with_invalid_size(self):
        """Test loading point cloud with size not divisible by 5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create file with 1003 floats (not divisible by 5)
            points = np.random.randn(1003).astype(np.float32)
            pc_file = tmpdir / 'invalid_size.bin'
            points.tofile(str(pc_file))
            
            reader = NuScenesDataReader(str(tmpdir), 'v1.0-test')
            
            # Should raise error during reshape
            with pytest.raises(RuntimeError, match="Failed to load point cloud"):
                reader.load_point_cloud(str(pc_file))


class TestDataReaderIntegration:
    """Integration tests combining multiple operations."""
    
    def test_load_info_and_point_clouds(self):
        """Test loading info file and corresponding point clouds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version = 'v1.0-test'
            version_dir = tmpdir / version
            version_dir.mkdir(parents=True)
            
            # Create point cloud files
            samples_dir = tmpdir / 'samples' / 'LIDAR_TOP'
            samples_dir.mkdir(parents=True)
            
            pc1 = np.random.randn(500, 5).astype(np.float32)
            pc2 = np.random.randn(600, 5).astype(np.float32)
            
            pc1_file = samples_dir / 'n000001.bin'
            pc2_file = samples_dir / 'n000002.bin'
            
            pc1.tofile(str(pc1_file))
            pc2.tofile(str(pc2_file))
            
            # Create info file referencing these point clouds
            frames = [
                {
                    'lidar_path': str(pc1_file),
                    'token': 'token1' * 6 + 'to',
                    'timestamp': 1234567890123456,
                    'gt_boxes': np.array([[1, 2, 3, 4, 5, 6, 0.5, 0.1, 0.2]], dtype=np.float32),
                    'gt_names': np.array(['car']),
                },
                {
                    'lidar_path': str(pc2_file),
                    'token': 'token2' * 6 + 'to',
                    'timestamp': 1234567890223456,
                    'gt_boxes': np.array([[2, 3, 4, 5, 6, 7, 1.0, 0.2, 0.3]], dtype=np.float32),
                    'gt_names': np.array(['pedestrian']),
                }
            ]
            
            info_file = version_dir / 'nuscenes_infos_1sweeps_train.pkl'
            with open(info_file, 'wb') as f:
                pickle.dump(frames, f)
            
            # Load info and point clouds
            reader = NuScenesDataReader(str(tmpdir), version)
            loaded_frames = reader.load_info_file('train')
            
            assert len(loaded_frames) == 2
            
            # Load point clouds
            pc1_loaded = reader.load_point_cloud(loaded_frames[0]['lidar_path'])
            pc2_loaded = reader.load_point_cloud(loaded_frames[1]['lidar_path'])
            
            assert pc1_loaded.shape == (500, 5)
            assert pc2_loaded.shape == (600, 5)
            np.testing.assert_array_almost_equal(pc1_loaded, pc1)
            np.testing.assert_array_almost_equal(pc2_loaded, pc2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
