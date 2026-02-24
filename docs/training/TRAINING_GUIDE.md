# Training Guide: CenterPoint on 8K Waymo Dataset

## Quick Start

```bash
./scripts/train_8k_waymo.sh
```

This will train CenterPoint on your converted 8K Waymo dataset for 30 epochs.

## Training Configuration

- **Model**: CenterPoint (single-stage)
- **Dataset**: 7,200 training frames, 800 validation frames
- **Batch Size**: 8 per GPU
- **Epochs**: 30
- **Learning Rate**: 0.003 (adam_onecycle)
- **Expected Time**: ~1-2 days on single GPU

## Manual Training Command

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 8 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed
```

## Training Parameters

### Adjust Batch Size (if GPU memory issues)

```bash
# Reduce to 4 if out of memory
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 4 \
    --epochs 30
```

### Multi-GPU Training

```bash
# Use 2 GPUs
bash scripts/dist_train.sh 2 \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 8 \
    --epochs 30
```

### Resume Training

```bash
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 8 \
    --epochs 30 \
    --ckpt path/to/checkpoint.pth
```

## Monitoring Training

### TensorBoard

```bash
tensorboard --logdir detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/tensorboard
```

### Check Logs

```bash
tail -f detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt
```

### Watch GPU Usage

```bash
watch -n 1 nvidia-smi
```

## Training Progress

Expected training metrics:

| Epoch | Train Loss | Val mAP | Time/Epoch |
|-------|-----------|---------|------------|
| 1     | ~2.5      | ~0.20   | ~2-3 hours |
| 10    | ~1.2      | ~0.45   | ~2-3 hours |
| 20    | ~0.8      | ~0.55   | ~2-3 hours |
| 30    | ~0.6      | ~0.60   | ~2-3 hours |

## Output Structure

```
detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/
├── ckpt/
│   ├── checkpoint_epoch_1.pth
│   ├── checkpoint_epoch_10.pth
│   ├── checkpoint_epoch_20.pth
│   └── checkpoint_epoch_30.pth
├── tensorboard/
│   └── events.out.tfevents.*
└── log_train_*.txt
```

## After Training

### Test the Model

```bash
cd detection
python tools/test.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --ckpt output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/ckpt/checkpoint_epoch_30.pth \
    --batch_size 1
```

### Run on Full Dataset

```bash
python tools/test.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --ckpt output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/ckpt/checkpoint_epoch_30.pth \
    --batch_size 1 \
    --save_to_file
```

This will save detection results for tracking and refinement.

## Troubleshooting

### Out of Memory

Reduce batch size:
```bash
--batch_size 4  # or even 2
```

### Slow Training

- Check GPU utilization with `nvidia-smi`
- Reduce workers if CPU bottleneck: `--workers 2`
- Use mixed precision training (if supported)

### NaN Loss

- Check learning rate (reduce if needed)
- Check data normalization
- Verify dataset integrity

### Poor Validation Performance

- Train for more epochs (try 50)
- Adjust learning rate schedule
- Check data augmentation settings

## Expected Improvements

Compared to the original 400-frame dataset:

| Metric | Old (400 frames, 12 epochs) | New (8K frames, 30 epochs) |
|--------|----------------------------|----------------------------|
| **Training Data** | 400 frames | 7,200 frames (18x more) |
| **mAP** | ~0.30 | ~0.60 (2x better) |
| **Boxes/Frame** | 9.5 | 15-20 (better recall) |
| **False Positives** | High | Low (better precision) |
| **Tracking Quality** | Broken | Continuous |
| **Refinement** | +321% false positives | +10-30% real detections |

## Next Steps After Training

1. **Evaluate** on validation set
2. **Run Detection** on all frames
3. **Run Tracking** on detection results
4. **Run Refinement** (GRM, PRM, CRM)
5. **Compare** with ablation study results

## Files Created

- `scripts/train_8k_waymo.sh` - Training script
- `detection/tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml` - Model config
- `detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml` - Dataset config
- `TRAINING_GUIDE.md` - This file

---

**Ready to train! Run `./scripts/train_8k_waymo.sh` to start.**
