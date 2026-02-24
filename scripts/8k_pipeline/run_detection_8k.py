#!/usr/bin/env python3
"""Run detection on 8K nuScenes dataset using the trained OpenPCDet model."""

import sys
import os
from pathlib import Path

# Get the project root directory (2 levels up from this script)
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

# Add modules to path
sys.path.insert(0, str(project_root / 'detection'))
sys.path.insert(0, str(project_root))

import argparse
import pickle
import torch
from detzero_utils.config_utils import cfg, cfg_from_yaml_file
from detzero_utils import common_utils
from detzero_det.datasets import build_dataloader
from detzero_det.models import build_network

def parse_args():
    parser = argparse.ArgumentParser(description='Run detection on 8K dataset')
    parser.add_argument('--cfg_file', type=str, 
                        default='detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml',
                        help='Config file')
    parser.add_argument('--ckpt', type=str,
                        default='detection/output/centerpoint_8k/checkpoint_epoch_80.pth',
                        help='Checkpoint file')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size')
    parser.add_argument('--workers', type=int, default=4, help='Number of workers')
    parser.add_argument('--output_dir', type=str, 
                        default='output_8k/detection',
                        help='Output directory')
    parser.add_argument('--split', type=str, default='val', 
                        choices=['train', 'val', 'test'],
                        help='Dataset split to process')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Load config
    cfg_from_yaml_file(args.cfg_file, cfg)
    
    # Create logger (log to both output dir and logs dir)
    logger = common_utils.create_logger(log_dir / 'detection_8k.log')
    logger.info('=' * 80)
    logger.info(f'Running detection on 8K nuScenes dataset')
    logger.info(f'Config: {args.cfg_file}')
    logger.info(f'Checkpoint: {args.ckpt}')
    logger.info(f'Split: {args.split}')
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
                if not isinstance(val, list):
                    batch_dict[key] = val.cuda()
            
            # Forward pass
            pred_dicts, _ = model(batch_dict)
            
            # Collect results
            for batch_idx, pred_dict in enumerate(pred_dicts):
                frame_id = batch_dict['frame_id'][batch_idx]
                
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
    output_file = output_dir / f'{args.split}_detections.pkl'
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
