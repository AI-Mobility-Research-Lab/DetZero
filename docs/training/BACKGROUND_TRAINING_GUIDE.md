# Background Training Guide

## Current Status

### GPU Usage
```
GPU: NVIDIA GeForce RTX 4060
Memory: 7544 MiB / 8188 MiB (92% used)
GPU Utilization: 53%
Temperature: 78°C
Power: 115W
```

**Good utilization!** The GPU is being used efficiently.

### Training Process Status
⚠️ **WARNING**: Training is currently running in a regular terminal session (pts/17), NOT in a persistent session. This means:
- ❌ Training WILL BE KILLED if SSH disconnects
- ❌ Training WILL BE KILLED if terminal closes
- ❌ Not safe for long-running jobs

## Making Training Persistent

You have 3 options to make training survive SSH disconnections:

### Option 1: Use tmux (Recommended - Already Installed)

You already have tmux installed! Here's how to use it:

#### Stop Current Training
```bash
# Find the training process
ps aux | grep train.py | grep -v grep

# Kill it (use the main PID, likely 241078)
kill 241078
```

#### Start Training in tmux
```bash
# Create a new tmux session named "training"
tmux new -s training

# Inside tmux, start training
cd /home/aimob/projects/DetZero
./scripts/train_8k_waymo.sh

# Detach from tmux (training continues in background)
# Press: Ctrl+B, then D
```

#### Reattach to tmux Session
```bash
# List tmux sessions
tmux ls

# Reattach to training session
tmux attach -t training

# Or shorthand
tmux a -t training
```

#### tmux Quick Reference
- `Ctrl+B, D` - Detach (leave session running)
- `Ctrl+B, C` - Create new window
- `Ctrl+B, N` - Next window
- `Ctrl+B, P` - Previous window
- `tmux kill-session -t training` - Kill session

### Option 2: Use screen

```bash
# Install screen (if not installed)
sudo apt install screen

# Start training in screen
screen -S training
cd /home/aimob/projects/DetZero
./scripts/train_8k_waymo.sh

# Detach: Ctrl+A, then D

# Reattach
screen -r training
```

### Option 3: Use nohup (Simple but Less Control)

```bash
# Start training with nohup
cd /home/aimob/projects/DetZero/detection
nohup python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 2 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed \
    > training.log 2>&1 &

# Check if running
ps aux | grep train.py

# Monitor logs
tail -f training.log

# Or use the DetZero log
tail -f output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt
```

## Recommended Action

**I strongly recommend using tmux (Option 1)** because:
1. ✅ Already installed on your system
2. ✅ Easy to reattach and monitor
3. ✅ Can see live training output
4. ✅ Can interact with training if needed
5. ✅ Survives SSH disconnections

## Steps to Migrate Current Training to tmux

```bash
# 1. Stop current training
kill 241078

# 2. Start tmux session
tmux new -s training

# 3. Navigate and start training
cd /home/aimob/projects/DetZero
./scripts/train_8k_waymo.sh

# 4. Detach from tmux
# Press: Ctrl+B, then D

# 5. You can now safely disconnect SSH
# Training will continue running

# 6. When you reconnect, reattach to see progress
tmux attach -t training
```

## Monitoring Training Remotely

Even after detaching, you can monitor training:

### Check GPU Usage
```bash
watch -n 1 nvidia-smi
```

### Check Training Logs
```bash
tail -f detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt
```

### Check Process Status
```bash
ps aux | grep train.py
```

### Check Checkpoints
```bash
ls -lh detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/ckpt/
```

## Training Will Resume From Checkpoint

If training gets interrupted, you can resume:

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 2 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed \
    --ckpt output/waymo_8k/centerpoint_1sweep_8k/waymo_8k/ckpt/checkpoint_epoch_X.pth
```

Replace `X` with the last saved epoch number.

## Current Training Progress

Based on the process start time (20:31), training has been running for about 7 minutes and is at iteration ~630/3600 for epoch 1.

**If you want to keep this training session**, you should migrate it to tmux NOW before any SSH issues occur.

---

**Action Required**: Migrate training to tmux to ensure it survives SSH disconnections!
