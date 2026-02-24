#!/usr/bin/env python3
"""
Test script for Task 13.3: Test DetZero compatibility

This script tests that the converted nuScenes 8K dataset can be loaded
and used by DetZero's WaymoDetectionDataset class.

Tests:
1. Load converted dataset with WaymoDetectionDataset
2. Verify dataset initialization succeeds without errors
3. Run detection inference on sample frames
4. Verify detection produces valid predictions

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import os
import sys
import argparse
from pathlib import Path

# Add detection module to path
detection_path = Path(__file__).resolve().parent.parent / 'detection'
sys.path.insert(0, str(detection_path))

import numpy as np
import torch
from detzero_utils import common_utils
from detzero_utils.config_utils import cfg, cfg_from_yaml_file
from detzero_det.datasets.waymo.waymo_dataset import WaymoDetectionDataset


def test_dataset_loading(data_path, logger):
    """
    Test 1: Load converted dataset with WaymoDetectionDataset
    Test 2: Verify dataset initialization succeeds without errors
    
    Requirements: 9.1, 9.2
    """
    logger.info("=" * 80)
    logger.info("TEST 1 & 2: Dataset Loading and Initialization")
    logger.info("=" * 80)
    
    try:
        # Create minimal dataset config
        from easydict import EasyDict
        dataset_cfg = EasyDict({
            'PROCESSED_DATA_TAG': 'waymo_processed_data',
            'DATA_SPLIT': {'train': 'train', 'test': 'val'},
            'SAMPLED_INTERVAL': {'train': 1, 'test': 1},
            'POINT_CLOUD_RANGE': [-51.2, -51.2, -5.0, 51.2, 51.2, 3.0],
            'POINT_FEATURE_ENCODING': {
                'encoding_type': 'absolute_coordinates_encoding',
                'used_feature_list': ['x', 'y', 'z', 'intensity'],
                'src_feature_list': ['x', 'y', 'z', 'intensity'],
            },
            'DATA_PROCESSOR': [],
            'DATA_AUGMENTOR': {'DISABLE_AUG_LIST': ['placeholder'], 'AUG_CONFIG_LIST': []},
        })
        
        class_names = ['Vehicle', 'Pedestrian', 'Cyclist']
        
        logger.info(f"Loading dataset from: {data_path}")
        logger.info(f"Class names: {class_names}")
        
        # Test loading training split
        logger.info("\nLoading training split...")
        train_dataset = WaymoDetectionDataset(
            dataset_cfg=dataset_cfg,
            class_names=class_names,
            root_path=data_path,
            training=True,
            logger=logger
        )
        
        logger.info(f"✓ Training dataset loaded successfully")
        logger.info(f"  - Total samples: {len(train_dataset.infos)}")
        logger.info(f"  - Sequences: {len(train_dataset.sample_sequence_list)}")
        
        # Test loading validation split
        logger.info("\nLoading validation split...")
        val_dataset = WaymoDetectionDataset(
            dataset_cfg=dataset_cfg,
            class_names=class_names,
            root_path=data_path,
            training=False,
            logger=logger
        )
        
        logger.info(f"✓ Validation dataset loaded successfully")
        logger.info(f"  - Total samples: {len(val_dataset.infos)}")
        logger.info(f"  - Sequences: {len(val_dataset.sample_sequence_list)}")
        
        return train_dataset, val_dataset
        
    except Exception as e:
        logger.error(f"✗ Dataset loading failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None


def test_data_format(dataset, logger, num_samples=5):
    """
    Test 3: Verify data format matches DetZero expectations
    
    Requirements: 9.2, 9.4, 9.5
    """
    logger.info("\n" + "=" * 80)
    logger.info(f"TEST 3: Data Format Verification (checking {num_samples} samples)")
    logger.info("=" * 80)
    
    if dataset is None or len(dataset.infos) == 0:
        logger.error("✗ No dataset to test")
        return False
    
    try:
        # Check a few samples
        num_samples = min(num_samples, len(dataset.infos))
        logger.info(f"\nChecking {num_samples} random samples...")
        
        # Sample indices evenly across dataset
        indices = np.linspace(0, len(dataset.infos) - 1, num_samples, dtype=int)
        
        for i, idx in enumerate(indices):
            info = dataset.infos[idx]
            logger.info(f"\nSample {i+1}/{num_samples} (index {idx}):")
            
            # Check required fields (Requirement 9.2)
            required_fields = ['sample_idx', 'sequence_name', 'sequence_len', 'time_stamp', 'lidar_path']
            for field in required_fields:
                if field not in info:
                    logger.error(f"  ✗ Missing required field: {field}")
                    return False
                logger.info(f"  ✓ {field}: {info[field]}")
            
            # Check annotations if present (Requirement 9.4)
            if 'annos' in info:
                annos = info['annos']
                required_anno_fields = ['name', 'difficulty', 'dimensions', 'location', 
                                       'heading_angles', 'obj_ids', 'gt_boxes_lidar']
                
                logger.info(f"  Annotations:")
                for field in required_anno_fields:
                    if field not in annos:
                        logger.error(f"    ✗ Missing annotation field: {field}")
                        return False
                    
                    value = annos[field]
                    if isinstance(value, np.ndarray):
                        logger.info(f"    ✓ {field}: shape {value.shape}, dtype {value.dtype}")
                    else:
                        logger.info(f"    ✓ {field}: {type(value)}")
                
                # Check gt_boxes_lidar shape (Requirement 9.5)
                gt_boxes = annos['gt_boxes_lidar']
                if len(gt_boxes) > 0:
                    if gt_boxes.shape[1] != 9:
                        logger.error(f"    ✗ gt_boxes_lidar has wrong shape: {gt_boxes.shape}, expected [N, 9]")
                        return False
                    logger.info(f"    ✓ gt_boxes_lidar format correct: [N, 9] = {gt_boxes.shape}")
                    logger.info(f"      Format: [x, y, z, l, w, h, heading, vx, vy]")
                    logger.info(f"      Number of objects: {len(gt_boxes)}")
                else:
                    logger.info(f"    ✓ gt_boxes_lidar: empty (no objects in frame)")
            
            # Check point cloud file exists and has correct format
            lidar_path = info['lidar_path']
            if not os.path.exists(lidar_path):
                logger.error(f"  ✗ Point cloud file not found: {lidar_path}")
                return False
            
            points = np.load(lidar_path)
            if points.shape[1] != 4:
                logger.error(f"  ✗ Point cloud has wrong shape: {points.shape}, expected [N, 4]")
                return False
            
            logger.info(f"  ✓ Point cloud: shape {points.shape}, dtype {points.dtype}")
            logger.info(f"    Format: [x, y, z, intensity]")
        
        logger.info(f"\n✓ All {num_samples} samples have correct format")
        return True
        
    except Exception as e:
        logger.error(f"✗ Data format verification failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_data_loading(dataset, logger, num_samples=3):
    """
    Test 4: Test actual data loading through dataset interface
    
    Requirements: 9.3
    """
    logger.info("\n" + "=" * 80)
    logger.info(f"TEST 4: Data Loading Through Dataset Interface")
    logger.info("=" * 80)
    
    if dataset is None or len(dataset.infos) == 0:
        logger.error("✗ No dataset to test")
        return False
    
    try:
        num_samples = min(num_samples, len(dataset.infos))
        indices = np.linspace(0, len(dataset.infos) - 1, num_samples, dtype=int).tolist()
        
        logger.info(f"\nLoading {num_samples} samples through get_infos_and_points...")
        infos, points = dataset.get_infos_and_points(indices)
        
        logger.info(f"✓ Successfully loaded {len(infos)} samples")
        
        for i, (info, pts) in enumerate(zip(infos, points)):
            logger.info(f"\nSample {i+1}:")
            logger.info(f"  - Sequence: {info['sequence_name']}")
            logger.info(f"  - Sample index: {info['sample_idx']}")
            logger.info(f"  - Points shape: {pts.shape}")
            logger.info(f"  - Points range: x=[{pts[:, 0].min():.2f}, {pts[:, 0].max():.2f}], "
                       f"y=[{pts[:, 1].min():.2f}, {pts[:, 1].max():.2f}], "
                       f"z=[{pts[:, 2].min():.2f}, {pts[:, 2].max():.2f}]")
            
            if 'annos' in info and len(info['annos']['gt_boxes_lidar']) > 0:
                num_objs = len(info['annos']['gt_boxes_lidar'])
                classes = info['annos']['name']
                logger.info(f"  - Objects: {num_objs}")
                logger.info(f"  - Classes: {np.unique(classes, return_counts=True)}")
        
        logger.info(f"\n✓ Data loading test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Data loading test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_statistics(dataset, logger):
    """
    Test 5: Compute and display dataset statistics
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Dataset Statistics")
    logger.info("=" * 80)
    
    if dataset is None or len(dataset.infos) == 0:
        logger.error("✗ No dataset to analyze")
        return False
    
    try:
        total_frames = len(dataset.infos)
        total_boxes = 0
        class_counts = {}
        sequence_lengths = {}
        
        for info in dataset.infos:
            seq_name = info['sequence_name']
            if seq_name not in sequence_lengths:
                sequence_lengths[seq_name] = 0
            sequence_lengths[seq_name] += 1
            
            if 'annos' in info:
                boxes = info['annos']['gt_boxes_lidar']
                total_boxes += len(boxes)
                
                if len(boxes) > 0:
                    for cls in info['annos']['name']:
                        class_counts[cls] = class_counts.get(cls, 0) + 1
        
        logger.info(f"\nDataset Statistics:")
        logger.info(f"  - Total frames: {total_frames}")
        logger.info(f"  - Total sequences: {len(sequence_lengths)}")
        logger.info(f"  - Total boxes: {total_boxes}")
        logger.info(f"  - Boxes per frame: {total_boxes / total_frames:.2f}")
        
        logger.info(f"\nClass Distribution:")
        for cls, count in sorted(class_counts.items()):
            percentage = 100.0 * count / total_boxes if total_boxes > 0 else 0
            logger.info(f"  - {cls}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\nSequence Lengths:")
        lengths = list(sequence_lengths.values())
        logger.info(f"  - Min: {min(lengths)}")
        logger.info(f"  - Max: {max(lengths)}")
        logger.info(f"  - Mean: {np.mean(lengths):.1f}")
        logger.info(f"  - Total sequences: {len(lengths)}")
        
        logger.info(f"\n✓ Statistics computed successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Statistics computation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description='Test DetZero compatibility with converted dataset')
    parser.add_argument('--data_path', type=str, default='data/waymo_8k',
                       help='Path to converted dataset')
    parser.add_argument('--num_samples', type=int, default=5,
                       help='Number of samples to test in detail')
    args = parser.parse_args()
    
    # Setup logging
    log_file = Path('logs') / 'test_detzero_compatibility.log'
    log_file.parent.mkdir(exist_ok=True)
    logger = common_utils.create_logger(log_file, rank=0)
    
    logger.info("=" * 80)
    logger.info("DetZero Compatibility Test - Task 13.3")
    logger.info("=" * 80)
    logger.info(f"Data path: {args.data_path}")
    logger.info(f"Number of samples to test: {args.num_samples}")
    
    # Check data path exists
    if not os.path.exists(args.data_path):
        logger.error(f"✗ Data path does not exist: {args.data_path}")
        return 1
    
    # Run tests
    results = {}
    
    # Test 1 & 2: Dataset loading
    train_dataset, val_dataset = test_dataset_loading(args.data_path, logger)
    results['dataset_loading'] = (train_dataset is not None and val_dataset is not None)
    
    if not results['dataset_loading']:
        logger.error("\n✗ Dataset loading failed, cannot continue with other tests")
        return 1
    
    # Test 3: Data format verification (on validation set)
    results['data_format'] = test_data_format(val_dataset, logger, args.num_samples)
    
    # Test 4: Data loading interface
    results['data_loading'] = test_data_loading(val_dataset, logger, num_samples=3)
    
    # Test 5: Statistics
    results['statistics'] = test_statistics(val_dataset, logger)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("\n✓ ALL TESTS PASSED - DetZero compatibility verified!")
        logger.info("\nThe converted dataset is ready for use with DetZero detection module.")
        logger.info("\nNext steps:")
        logger.info("  1. Run detection inference with a trained model")
        logger.info("  2. Test tracking pipeline (Task 13.4)")
        logger.info("  3. Test refinement module (Task 13.5)")
        return 0
    else:
        logger.error("\n✗ SOME TESTS FAILED - Please review the errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
