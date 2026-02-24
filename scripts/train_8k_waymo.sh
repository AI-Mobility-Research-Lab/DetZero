#!/bin/bash
# Training script for CenterPoint on 8K Waymo dataset

cd detection

# Training configuration
CFG_FILE="tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml"
BATCH_SIZE=1  # Reduced to 1 for 7.6 GB GPU
EPOCHS=30
WORKERS=1  # Reduced to 1 to minimize memory usage
EXTRA_TAG="waymo_8k"

# PyTorch memory optimization settings
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128
export CUDA_LAUNCH_BLOCKING=0
# Enable memory-efficient attention if available
export PYTORCH_ENABLE_MEM_EFFICIENT_ATTENTION=1

echo "=========================================="
echo "Training CenterPoint on 8K Waymo Dataset"
echo "=========================================="
echo "Config: $CFG_FILE"
echo "Batch size: $BATCH_SIZE"
echo "Epochs: $EPOCHS"
echo "Workers: $WORKERS (minimized for memory)"
echo "Tag: $EXTRA_TAG"
echo "Memory optimization:"
echo "  - expandable_segments:True"
echo "  - max_split_size_mb:128"
echo "  - Single worker to reduce memory overhead"
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
