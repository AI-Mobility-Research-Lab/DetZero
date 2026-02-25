# DetZero Training Guide - Quick Reference

## Current Status
- **Instance**: `detzero-v100-training` (V100 GPU, 16GB VRAM)
- **Zone**: `us-central1-a`
- **Project**: `detzeroaimob`
- **Dataset**: 8K frames at `~/waymo_8k` (72 train scenes, 8 val scenes)

## Fix Training Setup

The pickle files were empty due to incorrect generation. Run this to fix:

```bash
cd ~/DetZero
bash fix_training_setup.sh
```

This will:
1. Verify conda environment (Python 3.9, PyTorch 1.10)
2. Check dataset structure
3. Create necessary directories and symlinks
4. Generate pickle files with correct paths
5. Verify the generated files

## Start Training

### Option 1: Direct (see output immediately)
```bash
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh
```

### Option 2: With tmux (persistent, survives SSH disconnection)
```bash
# Start new tmux session
tmux new -s training

# Inside tmux, run training
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh

# Detach from tmux: Press Ctrl+B, then D
# Training continues in background

# Reattach later
tmux attach -t training

# Kill session when done
tmux kill-session -t training
```

## Training Details
- **Config**: CenterPoint 1-sweep
- **Batch size**: 4 (optimized for V100 16GB)
- **Epochs**: 30
- **Expected time**: ~4-5 hours
- **Output**: `detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/`

## Monitor Training

### Check GPU usage
```bash
watch -n 1 nvidia-smi
```

### View training logs (if using tmux)
```bash
tmux attach -t training
```

### Check output directory
```bash
ls -lh ~/DetZero/detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/
```

## Stop Instance (Save Costs!)

V100 costs ~$2.48/hour. Stop when not training:

```bash
# From your local machine
gcloud compute instances stop detzero-v100-training \
    --zone=us-central1-a \
    --project=detzeroaimob
```

## Restart Instance

```bash
# From your local machine
gcloud compute instances start detzero-v100-training \
    --zone=us-central1-a \
    --project=detzeroaimob

# SSH back in
gcloud compute ssh detzero-v100-training \
    --zone=us-central1-a \
    --project=detzeroaimob
```

## Troubleshooting

### Issue: Empty pickle files
**Solution**: Run `bash fix_training_setup.sh`

### Issue: FileNotFoundError during training
**Cause**: Paths in pickle files are incorrect
**Solution**: Regenerate pickle files with fix script

### Issue: CUDA out of memory
**Solution**: Reduce batch size in `scripts/train_8k_waymo_v100.sh`
```bash
BATCH_SIZE=2  # Instead of 4
```

### Issue: Training crashes immediately
**Check**:
1. Pickle files exist and have data: `ls -lh ~/DetZero/data/waymo_8k/*.pkl`
2. CUDA extensions built: `ls -lh detection/detzero_det/ops/iou3d_nms/*.so`
3. Environment activated: `conda activate detzero && which python`

### Issue: tmux session exits immediately
**Cause**: Script has syntax error or immediate failure
**Solution**: Run script directly first to see error:
```bash
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh
```

## Important Notes

1. **SSH Disconnection**: Training will stop if you run directly and SSH disconnects. Use tmux!
2. **Cost Management**: Always stop instance when not training
3. **Checkpoints**: Saved every epoch to output directory
4. **Resume Training**: Use `--ckpt` flag in train.py if needed

## Environment Details

- **Python**: 3.9 (conda)
- **PyTorch**: 1.10.0 with CUDA 11.1
- **NumPy**: <2.0 (1.26.4 recommended)
- **GCC**: 10 (for CUDA 11.1 compatibility)
- **CUDA Driver**: 580.126.09

## Quick Commands

```bash
# Activate environment
conda activate detzero

# Check environment
which python && python --version

# Check GPU
nvidia-smi

# Check dataset
ls -lh ~/waymo_8k/waymo_processed_data/ | head

# Check pickle files
python3 -c "import pickle; data=pickle.load(open('/home/aimob/DetZero/data/waymo_8k/waymo_infos_train.pkl','rb')); print(f'Train samples: {len(data)}')"

# Start training in tmux
tmux new -s training "cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh"

# Detach: Ctrl+B, D
# Reattach: tmux attach -t training
```
