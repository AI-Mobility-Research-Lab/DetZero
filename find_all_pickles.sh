#!/bin/bash
# Find all waymo pickle files and check their paths

echo "=========================================="
echo "Finding all waymo_infos_*.pkl files"
echo "=========================================="
echo ""

find ~ -name "waymo_infos_*.pkl" 2>/dev/null | while read pkl_file; do
    echo "Found: $pkl_file"
    ls -lh "$pkl_file"
    
    # Check the first path in the pickle file
    python3 << PYEOF
import pickle
import os
try:
    with open('$pkl_file', 'rb') as f:
        data = pickle.load(f)
    if len(data) > 0 and 'point_cloud' in data[0] and 'lidar_path' in data[0]['point_cloud']:
        path = data[0]['point_cloud']['lidar_path']
        exists = os.path.exists(path)
        print(f"  Samples: {len(data)}")
        print(f"  Sample path: {path}")
        print(f"  Exists: {exists}")
    else:
        print(f"  Samples: {len(data)} (empty or no path)")
except Exception as e:
    print(f"  Error: {e}")
PYEOF
    echo ""
done

echo "=========================================="
echo "Checking symlinks in data directory"
echo "=========================================="
ls -la ~/DetZero/data/waymo_8k/
