#!/usr/bin/env python3
"""Run detection using OpenPCDet directly on 8K nuScenes dataset."""

import sys
import os
from pathlib import Path

# Change to OpenPCDet directory
openpcdet_dir = Path('/home/aimob/projects/OpenPCDet')
os.chdir(openpcdet_dir)
sys.path.insert(0, str(openpcdet_dir))

import argparse
import pickle
import torch
import numpy as np
from pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import build_dataloader
from pcdet.models import build_network
from pcdet.utils import common_utils

def parse_args():
    parser = argparse.ArgumentParser(description='Run detection on 8K dataset')
    parser.add_argument('--cfg_file', type=str,
                        default='tools/cfgs/nuscenes_custom_models/centerpoint_8k.yaml',
                        help='Config file')
    parser.add_argument('--ckpt', type=str,
                        default='output/cfgs/nuscenes_custom_models/centerpoint_8k/centerpoint_8k_20260213_191157/ckpt/checkpoint_epoch_80.pth',
                        help='Checkpoint file')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size')
    parser.add_argument('--workers', type=int, default=4, help='Number of workers')
    parser.add_argument('--output_dir', type=str,
                        default='/home/aimob/projects/DetZero/output_8k/detection',
                        help='Output directory')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logs directory
    log_dir = Path('/home/aimob/projects/DetZero/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Load config
    cfg_from_yaml_file(args.cfg_file, cfg)
    cfg.TAG = Path(args.cfg_file).stem
    cfg.EXP_GROUP_PATH = '/'
    
    # Create logger
    logger = common_utils.create_logger(log_dir / 'detection_8k.log', rank=0)
    logger.info('=' * 80)
    logger.info(f'Running detection on 8K nuScenes dataset')
    logger.info(f'Config: {args.cfg_file}')
    logger.info(f'Checkpoint: {args.ckpt}')
    logger.info('=' * 80)
    
    # Build dataloader
    logger.info('Building dataloader...')
    test_set, test_loader, sampler = build_dataloader(
        dataset_cfg=cfg.DATA_CONFIG,
        class_names=cfg.CLASS_NAMES,
        batch_size=args.batch_size,
        dist=False,
        workers=args.workers,
        logger=logger,
        training=False
    )
    
    logger.info(f'Total samples: {len(test_set)}')
    
    # Build model
    logger.info('Building model...')
    model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=test_set)
    model.cuda()
    
    # Load checkpoint
    logger.info(f'Loading checkpoint from {args.ckpt}')
    checkpoint = torch.load(args.ckpt)
    model.load_state_dict(checkpoint['model_state'])
    model.eval()
    
    # Run inference
    logger.info('Running inference...')
    results = []
    
    with torch.no_grad():
        for i, batch_dict in enumerate(test_loader):
            if i % 10 == 0:
                logger.info(f'Processing batch {i}/{len(test_loader)}')
            
            # Move to GPU
            for key, val in batch_dict.items():
                if not isinstance(val, (list, np.ndarray)):
                    if isinstance(val, torch.Tensor):
                        batch_dict[key] = val.cuda()
            
            # Forward pass
            pred_dicts, _ = model(batch_dict)
            
            # Collect results
            for batch_idx, pred_dict in enumerate(pred_dicts):
                # Get frame info
                if 'frame_id' in batch_dict:
                    frame_id = batch_dict['frame_id'][batch_idx]
                elif 'metadata' in batch_dict and 'token' in batch_dict['metadata'][batch_idx]:
                    frame_id = batch_dict['metadata'][batch_idx]['token']
                else:
                    frame_id = f'frame_{len(results):06d}'
                
                result = {
                    'frame_id': frame_id,
                    'name': pred_dict['pred_labels'].cpu().numpy(),
                    'score': pred_dict['pred_scores'].cpu().numpy(),
                    'boxes_lidar': pred_dict['pred_boxes'].cpu().numpy(),
                }
                
                # Add metadata if available
                if 'metadata' in batch_dict:
                    result['metadata'] = batch_dict['metadata'][batch_idx]
                
                results.append(result)
    
    # Save results
    output_file = output_dir / 'val_detections.pkl'
    logger.info(f'Saving {len(results)} results to {output_file}')
    
    with open(output_file, 'wb') as f:
        pickle.dump(results, f)
    
    # Print statistics
    total_boxes = sum(len(r['score']) for r in results)
    avg_boxes = total_boxes / len(results)
    all_scores = [s for r in results for s in r['score']]
    
    logger.info('=' * 80)
    logger.info('Detection Statistics:')
    logger.info(f'  Total frames: {len(results)}')
    logger.info(f'  Total boxes: {total_boxes}')
    logger.info(f'  Avg boxes/frame: {avg_boxes:.2f}')
    logger.info(f'  Score range: [{min(all_scores):.3f}, {max(all_scores):.3f}]')
    logger.info(f'  Avg score: {sum(all_scores)/len(all_scores):.3f}')
    logger.info('=' * 80)
    logger.info(f'Results saved to: {output_file}')
    logger.info('Done!')

if __name__ == '__main__':
    main()
