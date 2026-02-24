#!/bin/bash
# Training script optimized for A100 GPU (40GB VRAM)

cd detection

# Training configuration for A100
CFG_FILE="tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml"
BATCH_SIZE=8  # A100 can handle much larger batch size
EPOCHS=30
WORKERS=8  # More workers for faster data loading
EXTRA_TAG="waymo_8k_a100"

# A100 optimization settings
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUDA_LAUNCH_BLOCKING=0
# Enable TF32 for faster training on A100
export NVIDIA_TF32_OVERRIDE=1

echo "=========================================="
echo "Training CenterPoint on A100"
echo "=========================================="
echo "Config: $CFG_FILE"
echo "Batch size: $BATCH_SIZE (optimized for A100 40GB)"
echo "Epochs: $EPOCHS"
echo "Workers: $WORKERS"
echo "Tag: $EXTRA_TAG"
echo "Optimizations:"
echo "  - TF32 enabled for faster training"
echo "  - Large batch size for better GPU utilization"
echo "  - Multiple workers for fast data loading"
echo "=========================================="

# Check GPU
nvidia-smi

echo ""
echo "Starting training..."

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
