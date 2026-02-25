#!/usr/bin/env python3
"""
Script to regenerate pickle files for the waymo_8k dataset.
This ensures the paths are correct and the files contain actual data.
"""
import os
import sys
import pickle
import numpy as np
from pathlib import Path

# Add detection module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'detection'))

def check_dataset_structure():
    """Check if the dataset structure is correct"""
    waymo_8k_path = Path('/home/aimob/waymo_8k')
    processed_data_path = waymo_8k_path / 'waymo_processed_data'
    
    print("Checking dataset structure...")
    print(f"Dataset path: {waymo_8k_path}")
    print(f"Exists: {waymo_8k_path.exists()}")
    
    if processed_data_path.exists():
        scenes = list(processed_data_path.glob('segment-*'))
        print(f"Found {len(scenes)} scenes in processed data")
        if scenes:
            print(f"Sample scene: {scenes[0].name}")
            npy_files = list(scenes[0].glob('*.npy'))
            print(f"  Contains {len(npy_files)} .npy files")
    else:
        print(f"Processed data path does not exist: {processed_data_path}")
    
    return waymo_8k_path.exists()

def main():
    print("=" * 60)
    print("Regenerating Waymo 8K Dataset Pickle Files")
    print("=" * 60)
    
    # Check dataset structure first
    if not check_dataset_structure():
        print("\nERROR: Dataset not found at /home/aimob/waymo_8k")
        print("Please ensure the dataset is uploaded and extracted correctly.")
        return 1
    
    print("\nGenerating pickle files using waymo_dataset.py...")
    print("This will create:")
    print("  - waymo_infos_train.pkl")
    print("  - waymo_infos_val.pkl")
    print("  - waymo_infos_test.pkl")
    print()
    
    # Change to detection directory
    os.chdir('detection')
    
    # Import and run the dataset creation
    try:
        from detzero_det.datasets.waymo.waymo_dataset import create_waymo_infos
        import argparse
        
        # Create args object
        class Args:
            cfg_file = 'tools/cfgs/det_dataset_cfgs/waymo_8k.yaml'
            func = 'create_waymo_infos'
        
        args = Args()
        
        # Run the creation function
        create_waymo_infos(
            dataset_cfg=None,
            class_names=None,
            data_path=Path('/home/aimob/waymo_8k'),
            save_path=Path('/home/aimob/DetZero/data/waymo_8k')
        )
        
        print("\n" + "=" * 60)
        print("Verifying generated files...")
        print("=" * 60)
        
        # Verify the generated files
        for split in ['train', 'val', 'test']:
            pkl_file = f'/home/aimob/DetZero/data/waymo_8k/waymo_infos_{split}.pkl'
            if os.path.exists(pkl_file):
                with open(pkl_file, 'rb') as f:
                    data = pickle.load(f)
                print(f"\n{split}.pkl:")
                print(f"  Samples: {len(data)}")
                if len(data) > 0:
                    sample = data[0]
                    if 'point_cloud' in sample and 'lidar_path' in sample['point_cloud']:
                        print(f"  Sample path: {sample['point_cloud']['lidar_path']}")
                        print(f"  Path exists: {os.path.exists(sample['point_cloud']['lidar_path'])}")
            else:
                print(f"\n{split}.pkl: NOT FOUND")
        
        print("\n" + "=" * 60)
        print("Done!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
