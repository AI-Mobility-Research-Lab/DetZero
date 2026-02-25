#!/usr/bin/env python3
"""
Fix pickle file paths - replace old paths with correct ones
"""
import pickle
import os
import sys

def fix_pickle_file(pkl_path, old_base, new_base):
    """Fix paths in a pickle file"""
    if not os.path.exists(pkl_path):
        print(f"File not found: {pkl_path}")
        return False
    
    print(f"Processing: {pkl_path}")
    
    # Load the pickle file
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    if len(data) == 0:
        print(f"  Empty file, skipping")
        return False
    
    # Fix paths in each sample
    fixed_count = 0
    for sample in data:
        if 'point_cloud' in sample and 'lidar_path' in sample['point_cloud']:
            old_path = sample['point_cloud']['lidar_path']
            if old_base in old_path:
                new_path = old_path.replace(old_base, new_base)
                sample['point_cloud']['lidar_path'] = new_path
                fixed_count += 1
    
    print(f"  Fixed {fixed_count} paths out of {len(data)} samples")
    
    # Save back
    with open(pkl_path, 'wb') as f:
        pickle.dump(data, f)
    
    # Verify
    sample_path = data[0]['point_cloud']['lidar_path']
    exists = os.path.exists(sample_path)
    print(f"  Sample path: {sample_path}")
    print(f"  Exists: {exists}")
    
    return exists

def main():
    old_base = '/home/aimob/projects/DetZero/data/waymo_8k'
    new_base = '/home/aimob/DetZero/data/waymo_8k'
    
    pkl_dir = '/home/aimob/DetZero/data/waymo_8k'
    
    print("=" * 60)
    print("Fixing pickle file paths")
    print("=" * 60)
    print(f"Old base: {old_base}")
    print(f"New base: {new_base}")
    print(f"Directory: {pkl_dir}")
    print()
    
    success = True
    for split in ['train', 'val', 'test']:
        pkl_file = os.path.join(pkl_dir, f'waymo_infos_{split}.pkl')
        if os.path.exists(pkl_file):
            if not fix_pickle_file(pkl_file, old_base, new_base):
                success = False
        else:
            print(f"Not found: {pkl_file}")
        print()
    
    if success:
        print("=" * 60)
        print("SUCCESS! All pickle files fixed and verified")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("ERROR: Some files could not be fixed")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
