#!/bin/bash
# Check the per-sequence pickle files

echo "Checking per-sequence pickle files..."
echo ""

# Find a few sequence pickle files
find ~/DetZero/data/waymo_8k/waymo_processed_data -name "*.pkl" | head -5 | while read pkl_file; do
    echo "Found: $pkl_file"
    
    python3 << PYEOF
import pickle
import os

try:
    with open('$pkl_file', 'rb') as f:
        data = pickle.load(f)
    if len(data) > 0 and 'point_cloud' in data[0] and 'lidar_path' in data[0]['point_cloud']:
        path = data[0]['point_cloud']['lidar_path']
        print(f"  Samples: {len(data)}")
        print(f"  Sample path: {path}")
        print(f"  Has wrong path: {'/home/aimob/projects/DetZero/' in path}")
    else:
        print(f"  Samples: {len(data)}")
except Exception as e:
    print(f"  Error: {e}")
PYEOF
    echo ""
done

echo "Total sequence pickle files:"
find ~/DetZero/data/waymo_8k/waymo_processed_data -name "*.pkl" | wc -l
