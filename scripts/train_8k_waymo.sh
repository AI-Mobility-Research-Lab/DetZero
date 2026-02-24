#!/bin/bash
# Training script for CenterPoint on 8K Waymo dataset

cd detection

# Training configuration
CFG_FILE="tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml"
BATCH_SIZE=1  # Reduced to 1 for 7.6 GB GPU (batch_size=2 caused OOM)
EPOCHS=30
WORKERS=2  # Reduced from 4 to 2 to save memory
EXTRA_TAG="waymo_8k"

# PyTorch memory optimization settings
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUDA_LAUNCH_BLOCKING=0

echo "=========================================="
echo "Training CenterPoint on 8K Waymo Dataset"
echo "=========================================="
echo "Config: $CFG_FILE"
echo "Batch size: $BATCH_SIZE"
echo "Epochs: $EPOCHS"
echo "Workers: $WORKERS (reduced to save memory)"
echo "Tag: $EXTRA_TAG"
echo "Memory optimization: PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
echo "=========================================="

# Run training
python tools/train.py \
    --cfg_file $CFG_FILE \
    --batch_size $BATCH_SIZE \
    --epochs $EPOCHS \
    --workers $WORKERS \
    --extra_tag $EXTRA_TAG \
    --fix_random_seed

echo ""
echo "Training complete!"
echo "Checkpoint saved to: output/waymo_8k/centerpoint_1sweep_8k/$EXTRA_TAG/"
