#!/bin/bash
# Training script optimized for V100 GPU (16GB VRAM)

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate detzero

cd detection

# Training configuration for V100
CFG_FILE="tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml"
BATCH_SIZE=2  # Reduced to 2 to avoid OOM on V100 16GB
EPOCHS=30
WORKERS=6
EXTRA_TAG="waymo_8k_v100"

# V100 optimization settings
# Note: expandable_segments not supported in PyTorch 1.10
export CUDA_LAUNCH_BLOCKING=0

echo "=========================================="
echo "Training CenterPoint on V100"
echo "=========================================="
echo "Config: $CFG_FILE"
echo "Batch size: $BATCH_SIZE (reduced to avoid OOM)"
echo "Epochs: $EPOCHS"
echo "Workers: $WORKERS"
echo "Tag: $EXTRA_TAG"
echo "Expected training time: ~8-10 hours (with batch size 2)"
echo "=========================================="

# Check GPU
nvidia-smi

echo ""
echo "Starting training..."

# Run training
python3 tools/train.py \
    --cfg_file $CFG_FILE \
    --batch_size $BATCH_SIZE \
    --epochs $EPOCHS \
    --workers $WORKERS \
    --extra_tag $EXTRA_TAG \
    --fix_random_seed

echo ""
echo "Training complete!"
echo "Checkpoint saved to: output/waymo_8k/centerpoint_1sweep_8k/$EXTRA_TAG/"
