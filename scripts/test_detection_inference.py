#!/usr/bin/env python3
"""
Test detection inference on converted dataset

This script tests that DetZero can run detection inference on the converted
nuScenes 8K dataset and produce valid predictions.

Requirements: 9.3, 9.4, 9.5
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
from detzero_det.datasets import build_dataloader
from detzero_det.models import build_network


def test_detection_inference(cfg_file, ckpt_file, data_path, num_samples, logger):
    """
    Test detection inference on sample frames
    
    Requirements: 9.3, 9.4, 9.5
    """
    logger.info("=" * 80)
    logger.info("Detection Inference Test")
    logger.info("=" * 80)
    logger.info(f"Config: {cfg_file}")
    logger.info(f"Checkpoint: {ckpt_file}")
    logger.info(f"Data path: {data_path}")
    logger.info(f"Testing {num_samples} samples")
    
    try:
        # Load config
        cfg_from_yaml_file(cfg_file, cfg)
        cfg.ROOT_DIR = detection_path
        cfg.DATA_CONFIG.DATA_PATH = data_path
        
        logger.info("\n1. Building dataloader...")
        test_set, test_loader, sampler = build_dataloader(
            dataset_cfg=cfg.DATA_CONFIG,
            class_names=cfg.CLASS_NAMES,
            batch_size=1,
            dist=False,
            workers=0,  # Use 0 workers to avoid multiprocessing issues
            logger=logger,
            training=False
        )
        logger.info(f"✓ Dataloader built successfully")
        logger.info(f"  - Dataset size: {len(test_set)}")
        logger.info(f"  - Class names: {cfg.CLASS_NAMES}")
        
        # Build model
        logger.info("\n2. Building detection model...")
        model = build_network(
            model_cfg=cfg.MODEL,
            num_class=len(cfg.CLASS_NAMES),
            dataset=test_set
        )
        logger.info(f"✓ Model built successfully")
        
        # Load checkpoint
        logger.info("\n3. Loading checkpoint...")
        from detzero_utils.model_utils import load_params_from_file
        load_params_from_file(model, filename=ckpt_file, logger=logger, to_cpu=False)
        model.cuda()
        model.eval()
        logger.info(f"✓ Checkpoint loaded successfully")
        
        # Run inference on sample frames
        logger.info(f"\n4. Running inference on {num_samples} samples...")
        
        with torch.no_grad():
            for i, batch_dict in enumerate(test_loader):
                if i >= num_samples:
                    break
                
                # Move to GPU
                for key, val in batch_dict.items():
                    if not isinstance(val, np.ndarray):
                        continue
                    # Skip string arrays and metadata
                    if key in ['frame_id', 'metadata', 'calib', 'sequence_name']:
                        continue
                    # Skip string dtype arrays
                    if val.dtype.kind in ['U', 'S', 'O']:  # Unicode, byte string, or object
                        continue
                    batch_dict[key] = torch.from_numpy(val).float().cuda()
                
                # Run inference
                pred_dicts, ret_dict = model(batch_dict)
                
                # Validate predictions
                logger.info(f"\nSample {i+1}/{num_samples}:")
                logger.info(f"  - Frame ID: {batch_dict.get('frame_id', ['unknown'])[0]}")
                
                if len(pred_dicts) > 0:
                    pred = pred_dicts[0]
                    
                    # Check required fields
                    required_fields = ['pred_boxes', 'pred_scores', 'pred_labels']
                    for field in required_fields:
                        if field not in pred:
                            logger.error(f"  ✗ Missing prediction field: {field}")
                            return False
                    
                    pred_boxes = pred['pred_boxes']
                    pred_scores = pred['pred_scores']
                    pred_labels = pred['pred_labels']
                    
                    logger.info(f"  ✓ Predictions generated successfully")
                    logger.info(f"    - Predicted boxes: {len(pred_boxes)}")
                    logger.info(f"    - Box shape: {pred_boxes.shape}")
                    
                    if len(pred_boxes) > 0:
                        logger.info(f"    - Score range: [{pred_scores.min():.3f}, {pred_scores.max():.3f}]")
                        logger.info(f"    - Labels: {torch.unique(pred_labels).cpu().numpy()}")
                    else:
                        logger.info(f"    - No detections (empty frame or low confidence)")
                    
                    # Validate box format (should be [x, y, z, l, w, h, heading])
                    if pred_boxes.shape[1] != 7:
                        logger.error(f"  ✗ Invalid box shape: {pred_boxes.shape}, expected [N, 7]")
                        return False
                    
                    logger.info(f"    ✓ Box format correct: [N, 7] = {pred_boxes.shape}")
                    
                    # Check if predictions are valid (not NaN or Inf)
                    if torch.isnan(pred_boxes).any() or torch.isinf(pred_boxes).any():
                        logger.error(f"  ✗ Predictions contain NaN or Inf values")
                        return False
                    
                    logger.info(f"    ✓ All predictions are valid (no NaN/Inf)")
                    
                    # Show some example predictions
                    if len(pred_boxes) > 0:
                        logger.info(f"    Example predictions:")
                        for j in range(min(3, len(pred_boxes))):
                            box = pred_boxes[j].cpu().numpy()
                            score = pred_scores[j].cpu().item()
                            label = pred_labels[j].cpu().item()
                            class_name = cfg.CLASS_NAMES[int(label) - 1] if label > 0 else 'unknown'
                            logger.info(f"      {j+1}. {class_name}: score={score:.3f}, "
                                      f"center=({box[0]:.2f}, {box[1]:.2f}, {box[2]:.2f}), "
                                      f"size=({box[3]:.2f}, {box[4]:.2f}, {box[5]:.2f})")
                else:
                    logger.info(f"  ✓ No predictions (empty frame or low confidence)")
        
        logger.info(f"\n✓ Detection inference test passed!")
        logger.info(f"  - All {num_samples} samples processed successfully")
        logger.info(f"  - Predictions have valid format")
        logger.info(f"  - No format errors detected")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Detection inference test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description='Test detection inference on converted dataset')
    parser.add_argument('--cfg_file', type=str, 
                       default='detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml',
                       help='Config file for detection model')
    parser.add_argument('--ckpt', type=str,
                       default='detection/output/centerpoint_8k/checkpoint_epoch_80.pth',
                       help='Checkpoint file')
    parser.add_argument('--data_path', type=str, default='data/waymo_8k',
                       help='Path to converted dataset')
    parser.add_argument('--num_samples', type=int, default=5,
                       help='Number of samples to test')
    args = parser.parse_args()
    
    # Setup logging
    log_file = Path('logs') / 'test_detection_inference.log'
    log_file.parent.mkdir(exist_ok=True)
    logger = common_utils.create_logger(log_file, rank=0)
    
    logger.info("=" * 80)
    logger.info("DetZero Detection Inference Test - Task 13.3")
    logger.info("=" * 80)
    
    # Check files exist
    if not os.path.exists(args.cfg_file):
        logger.error(f"✗ Config file not found: {args.cfg_file}")
        return 1
    
    if not os.path.exists(args.ckpt):
        logger.error(f"✗ Checkpoint not found: {args.ckpt}")
        return 1
    
    if not os.path.exists(args.data_path):
        logger.error(f"✗ Data path not found: {args.data_path}")
        return 1
    
    # Run test
    success = test_detection_inference(
        args.cfg_file,
        args.ckpt,
        args.data_path,
        args.num_samples,
        logger
    )
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nDetZero can successfully:")
        logger.info("  1. Load the converted dataset")
        logger.info("  2. Initialize without errors")
        logger.info("  3. Run detection inference")
        logger.info("  4. Produce valid predictions")
        logger.info("\nThe converted dataset is fully compatible with DetZero!")
        return 0
    else:
        logger.error("\n" + "=" * 80)
        logger.error("✗ TEST FAILED")
        logger.error("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
