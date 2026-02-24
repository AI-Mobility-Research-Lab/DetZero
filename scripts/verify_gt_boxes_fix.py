#!/usr/bin/env python3
"""
Verify that all gt_boxes arrays have correct 2D shape [N, 9]
"""

import pickle
import numpy as np
from pathlib import Path
from tqdm import tqdm

def check_gt_boxes_shape(pkl_file):
    """Check if gt_boxes has correct shape"""
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    
    gt_boxes = data.get('gt_boxes_lidar', np.array([]))
    
    # Check if it's 1D when it should be 2D
    if gt_boxes.ndim == 1 and len(gt_boxes) == 0:
        return False, pkl_file, gt_boxes.shape
    
    # Should be 2D with shape [N, 9]
    if gt_boxes.ndim == 2 and gt_boxes.shape[1] == 9:
        return True, pkl_file, gt_boxes.shape
    
    return False, pkl_file, gt_boxes.shape

def main():
    data_dir = Path('data/waymo_8k/waymo_processed_data')
    
    # Find all pkl files
    pkl_files = list(data_dir.rglob('*.pkl'))
    print(f"Found {len(pkl_files)} pkl files")
    
    issues = []
    
    for pkl_file in tqdm(pkl_files, desc="Checking gt_boxes shapes"):
        is_valid, file_path, shape = check_gt_boxes_shape(pkl_file)
        if not is_valid:
            issues.append((file_path, shape))
    
    if issues:
        print(f"\n❌ Found {len(issues)} files with incorrect gt_boxes shape:")
        for file_path, shape in issues:
            print(f"  {file_path.relative_to(data_dir)}: shape={shape}")
        return False
    else:
        print("\n✅ All gt_boxes arrays have correct 2D shape [N, 9]")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
