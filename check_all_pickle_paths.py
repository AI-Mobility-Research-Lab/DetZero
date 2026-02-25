#!/usr/bin/env python3
"""
Check ALL paths in pickle files to find any with wrong paths
"""
import pickle
import os

pkl_file = '/home/aimob/DetZero/data/waymo_8k/waymo_infos_train.pkl'

print(f"Checking: {pkl_file}")
print()

with open(pkl_file, 'rb') as f:
    data = pickle.load(f)

print(f"Total samples: {len(data)}")
print()

# Check for wrong paths
wrong_paths = []
for i, sample in enumerate(data):
    if 'point_cloud' in sample and 'lidar_path' in sample['point_cloud']:
        path = sample['point_cloud']['lidar_path']
        if '/home/aimob/projects/DetZero/' in path:
            wrong_paths.append((i, path))

if wrong_paths:
    print(f"Found {len(wrong_paths)} samples with WRONG paths:")
    for i, path in wrong_paths[:10]:  # Show first 10
        print(f"  Sample {i}: {path}")
    if len(wrong_paths) > 10:
        print(f"  ... and {len(wrong_paths) - 10} more")
else:
    print("✓ All paths are correct!")
    print(f"Sample paths use: {data[0]['point_cloud']['lidar_path'][:50]}...")
