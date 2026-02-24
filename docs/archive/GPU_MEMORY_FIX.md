# GPU Memory Fix

## Problem

CUDA out of memory error with batch size 8 on RTX 4060 (7.6 GB).

## Solution

Reduced batch size from 8 to 2 to fit in available GPU memory.

## Updated Training Command

```bash
./scripts/train_8k_waymo.sh
```

Now uses batch size 2 instead of 8.

## Manual Training with Different Batch Sizes

### Batch Size 2 (Recommended for 7.6 GB GPU)

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 2 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed
```

### Batch Size 1 (If still out of memory)

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 1 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed
```

### Batch Size 4 (If you have more GPU memory)

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 4 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed
```

## Impact of Reduced Batch Size

### Training Time
- **Batch size 8**: ~1-2 days
- **Batch size 2**: ~2-3 days (4x more iterations)
- **Batch size 1**: ~3-4 days (8x more iterations)

### Model Quality
- Smaller batch sizes can actually improve generalization
- May need to adjust learning rate (already optimized in config)
- Final model quality should be similar or better

## Memory Usage by Batch Size

| Batch Size | GPU Memory | Training Time | Recommended For |
|------------|-----------|---------------|-----------------|
| 1 | ~3-4 GB | 3-4 days | 4-6 GB GPUs |
| 2 | ~5-6 GB | 2-3 days | 6-8 GB GPUs (RTX 4060) |
| 4 | ~8-10 GB | 1.5-2 days | 10-12 GB GPUs |
| 8 | ~14-16 GB | 1-2 days | 16+ GB GPUs |

## Alternative: Use PyTorch Memory Optimization

Try setting this environment variable before training:

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
./scripts/train_8k_waymo.sh
```

This may help with memory fragmentation.

## Monitor GPU Memory

Watch GPU memory usage during training:

```bash
watch -n 1 nvidia-smi
```

You should see:
- Memory usage: ~5-6 GB with batch size 2
- GPU utilization: 90-100%

## Resume Training

If training was interrupted, you can resume from the last checkpoint:

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 2 \
    --epochs 30 \
    --ckpt output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/ckpt/checkpoint_epoch_X.pth
```

Replace X with the last completed epoch number.

---

**The training script has been updated to use batch size 2. Run `./scripts/train_8k_waymo.sh` to start training.**
