#!/usr/bin/env python3
"""
Fix paths in ALL per-sequence pickle files
"""
import pickle
import os
import glob

old_base = '/home/aimob/projects/DetZero/data/waymo_8k'
new_base = '/home/aimob/DetZero/data/waymo_8k'

# Find all per-sequence pickle files
pkl_pattern = '/home/aimob/DetZero/data/waymo_8k/waymo_processed_data/*/segment-*.pkl'
pkl_files = glob.glob(pkl_pattern)

print("=" * 60)
print(f"Fixing {len(pkl_files)} per-sequence pickle files")
print("=" * 60)
print(f"Old base: {old_base}")
print(f"New base: {new_base}")
print()

fixed_count = 0
error_count = 0

for pkl_file in pkl_files:
    try:
        # Load the pickle file
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        
        if len(data) == 0:
            continue
        
        # Fix paths in each sample
        sample_fixed = 0
        for sample in data:
            if 'lidar_path' in sample:
                old_path = sample['lidar_path']
                if old_base in old_path:
                    sample['lidar_path'] = old_path.replace(old_base, new_base)
                    sample_fixed += 1
        
        if sample_fixed > 0:
            # Save back
            with open(pkl_file, 'wb') as f:
                pickle.dump(data, f)
            fixed_count += 1
            
            if fixed_count <= 5 or fixed_count % 10 == 0:
                print(f"Fixed {fixed_count}/{len(pkl_files)}: {os.path.basename(os.path.dirname(pkl_file))}")
    
    except Exception as e:
        print(f"Error processing {pkl_file}: {e}")
        error_count += 1

print()
print("=" * 60)
print(f"Fixed {fixed_count} files")
print(f"Errors: {error_count}")
print("=" * 60)
print()

# Verify a few files
print("Verifying fixes...")
for pkl_file in pkl_files[:3]:
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    if len(data) > 0 and 'lidar_path' in data[0]:
        path = data[0]['lidar_path']
        exists = os.path.exists(path)
        print(f"  {os.path.basename(pkl_file)}")
        print(f"    Path: {path[:80]}...")
        print(f"    Exists: {exists}")

print()
print("Done! You can now start training.")
