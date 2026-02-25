#!/bin/bash
# Script to fix all training setup issues

set -e  # Exit on error

echo "=========================================="
echo "DetZero Training Setup Fix"
echo "=========================================="

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate detzero

echo ""
echo "Step 1: Verify conda environment"
echo "----------------------------------------"
which python
python --version
which pip
pip --version

echo ""
echo "Step 2: Check dataset structure"
echo "----------------------------------------"
ls -lh ~/waymo_8k/ | head -20
echo ""
echo "Checking for processed data..."
if [ -d ~/waymo_8k/waymo_processed_data ]; then
    echo "✓ Processed data directory exists"
    scene_count=$(ls -d ~/waymo_8k/waymo_processed_data/segment-* 2>/dev/null | wc -l)
    echo "  Found $scene_count scenes"
else
    echo "✗ Processed data directory NOT found"
    echo "  Expected: ~/waymo_8k/waymo_processed_data"
fi

echo ""
echo "Step 3: Ensure data directory exists"
echo "----------------------------------------"
mkdir -p ~/DetZero/data/waymo_8k
echo "✓ Created ~/DetZero/data/waymo_8k"

echo ""
echo "Step 4: Create symlink if needed"
echo "----------------------------------------"
if [ ! -L ~/DetZero/data/waymo_8k/waymo_processed_data ]; then
    if [ -d ~/waymo_8k/waymo_processed_data ]; then
        ln -sf ~/waymo_8k/waymo_processed_data ~/DetZero/data/waymo_8k/waymo_processed_data
        echo "✓ Created symlink to processed data"
    else
        echo "⚠ Cannot create symlink - source directory not found"
    fi
else
    echo "✓ Symlink already exists"
fi

echo ""
echo "Step 5: Generate pickle files"
echo "----------------------------------------"
cd ~/DetZero/detection

python -m detzero_det.datasets.waymo.waymo_dataset \
    --func create_waymo_infos \
    --cfg_file tools/cfgs/det_dataset_cfgs/waymo_8k.yaml

echo ""
echo "Step 6: Verify pickle files"
echo "----------------------------------------"
python3 << 'PYEOF'
import pickle
import os

for split in ['train', 'val', 'test']:
    pkl_file = f'/home/aimob/DetZero/data/waymo_8k/waymo_infos_{split}.pkl'
    if os.path.exists(pkl_file):
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        print(f"{split}.pkl: {len(data)} samples")
        if len(data) > 0:
            sample = data[0]
            if 'point_cloud' in sample and 'lidar_path' in sample['point_cloud']:
                path = sample['point_cloud']['lidar_path']
                exists = os.path.exists(path)
                print(f"  Sample path: {path}")
                print(f"  Exists: {exists}")
    else:
        print(f"{split}.pkl: NOT FOUND")
PYEOF

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the output above to ensure pickle files have data"
echo "2. Start training with: bash scripts/train_8k_waymo_v100.sh"
echo "3. For persistent training, use tmux:"
echo "   tmux new -s training"
echo "   bash scripts/train_8k_waymo_v100.sh"
echo "   # Detach with Ctrl+B, D"
echo ""
