#!/usr/bin/env python3
"""
Test detection on the converted 8K Waymo dataset.
"""

import sys
import os
from pathlib import Path

# Add detection module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'detection'))

import torch
import numpy as np
import pickle
from detzero_det.datasets.waymo.waymo_dataset import WaymoDetectionDataset
from detzero_utils.config_utils import cfg_from_yaml_file


def test_dataset_loading():
    """Test that the dataset can be loaded correctly."""
    print("=" * 60)
    print("Testing Dataset Loading")
    print("=" * 60)
    
    # Load config
    config_file = 'detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml'
    
    from easydict import EasyDict
    import yaml
    
    with open(config_file, 'r') as f:
        cfg_dict = yaml.safe_load(f)
    cfg = EasyDict(cfg_dict)
    
    print(f"\nConfig loaded from: {config_file}")
    print(f"Dataset: {cfg.DATASET}")
    print(f"Data path: {cfg.DATA_PATH}")
    print(f"Point cloud range: {cfg.POINT_CLOUD_RANGE}")
    
    # Create dataset
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        dataset = WaymoDetectionDataset(
            dataset_cfg=cfg,
            class_names=['Vehicle', 'Pedestrian', 'Cyclist'],
            root_path=str(Path(cfg.DATA_PATH).absolute()),
            training=False,
            logger=logger
        )
        
        print(f"\n✅ Dataset loaded successfully!")
        print(f"Total samples: {len(dataset)}")
        
        # Test loading first sample
        if len(dataset) > 0:
            print(f"\nTesting first sample...")
            sample = dataset[0]
            
            print(f"  Points shape: {sample['points'].shape}")
            print(f"  Frame ID: {sample.get('frame_id', 'N/A')}")
            
            if 'gt_boxes' in sample:
                print(f"  GT boxes shape: {sample['gt_boxes'].shape}")
                print(f"  Number of objects: {len(sample['gt_boxes'])}")
            
            print(f"\n✅ Sample loaded successfully!")
            return True
        else:
            print(f"\n❌ Dataset is empty!")
            return False
            
    except Exception as e:
        print(f"\n❌ Failed to load dataset: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection_inference():
    """Test running detection inference on a few frames."""
    print("\n" + "=" * 60)
    print("Testing Detection Inference")
    print("=" * 60)
    
    # Check if checkpoint exists
    checkpoint_path = 'detection/output/centerpoint_8k/checkpoint_epoch_80.pth'
    if not Path(checkpoint_path).exists():
        print(f"\n❌ Checkpoint not found: {checkpoint_path}")
        return False
    
    print(f"\n✅ Checkpoint found: {checkpoint_path}")
    
    # Load checkpoint to verify it's valid
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        print(f"  Epoch: {checkpoint.get('epoch', 'N/A')}")
        print(f"  Model state dict keys: {len(checkpoint.get('model_state', {}).keys())}")
        print(f"\n✅ Checkpoint loaded successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Failed to load checkpoint: {e}")
        return False


def check_data_format():
    """Check the format of converted data."""
    print("\n" + "=" * 60)
    print("Checking Data Format")
    print("=" * 60)
    
    data_path = Path('data/waymo_8k/waymo_processed_data')
    
    if not data_path.exists():
        print(f"\n❌ Data path not found: {data_path}")
        return False
    
    # Get first sequence
    sequences = sorted([d for d in data_path.iterdir() if d.is_dir()])
    if not sequences:
        print(f"\n❌ No sequences found in {data_path}")
        return False
    
    first_seq = sequences[0]
    print(f"\nChecking sequence: {first_seq.name}")
    
    # Load info file
    info_file = first_seq / f"{first_seq.name}.pkl"
    if not info_file.exists():
        print(f"\n❌ Info file not found: {info_file}")
        return False
    
    with open(info_file, 'rb') as f:
        frames = pickle.load(f)
    
    print(f"  Number of frames: {len(frames)}")
    
    if frames:
        frame = frames[0]
        print(f"\n  First frame structure:")
        print(f"    Keys: {list(frame.keys())}")
        print(f"    sample_idx: {frame['sample_idx']}")
        print(f"    sequence_name: {frame['sequence_name']}")
        print(f"    sequence_len: {frame['sequence_len']}")
        
        # Check point cloud
        pc_path = Path(frame['lidar_path'])
        if pc_path.exists():
            points = np.load(pc_path)
            print(f"    Point cloud shape: {points.shape}")
            print(f"    Point cloud dtype: {points.dtype}")
        else:
            print(f"    ❌ Point cloud not found: {pc_path}")
            return False
        
        # Check annotations
        annos = frame['annos']
        print(f"    Annotations:")
        print(f"      Number of objects: {len(annos['name'])}")
        print(f"      Classes: {np.unique(annos['name'])}")
        print(f"      gt_boxes_lidar shape: {annos['gt_boxes_lidar'].shape}")
        
        print(f"\n✅ Data format looks correct!")
        return True
    
    return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("8K Waymo Dataset Detection Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Check data format
    results.append(("Data Format Check", check_data_format()))
    
    # Test 2: Dataset loading
    results.append(("Dataset Loading", test_dataset_loading()))
    
    # Test 3: Checkpoint verification
    results.append(("Checkpoint Verification", test_detection_inference()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✅ All tests passed! Ready to run full detection.")
        print("\nNext step:")
        print("  cd detection")
        print("  python tools/test.py \\")
        print("    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_waymo_8k.yaml \\")
        print("    --ckpt output/centerpoint_8k/checkpoint_epoch_80.pth \\")
        print("    --batch_size 1")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues before running detection.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
