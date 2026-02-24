# OOM (Out of Memory) Fix Summary

## Problem

Training kept crashing with `torch.OutOfMemoryError: CUDA out of memory` on 8GB GPU (RTX 4060).

### Crash History
1. **First crash** (~18 min): Memory usage 7.1 GB / 7.6 GB (93%)
2. **Second crash** (~20 min): Memory usage 6.8 GB / 7.6 GB (89%)

## Root Cause

Even with batch_size=1, the model's memory usage gradually increased during training due to:
1. Memory fragmentation in CUDA allocator
2. Multiple data loading workers consuming memory
3. Tensors not being released promptly after use
4. Gradient computation requiring additional memory

## Solution Applied

### 1. PyTorch CUDA Allocator Optimization
```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128
```
- `expandable_segments:True`: Reduces memory fragmentation
- `max_split_size_mb:128`: Limits maximum allocation size to prevent large fragmented blocks

### 2. Reduce Data Loading Workers
```bash
WORKERS=1  # Reduced from 4 → 2 → 1
```
- Each worker process consumes additional memory
- Single worker minimizes overhead while still loading data

### 3. Explicit Memory Cleanup in Training Loop
```python
# Save loss value before clearing
loss_val = loss.item()

# ... logging ...

# Clear memory after logging
del loss, tb_dict, batch
if accumulated_iter % 10 == 0:
    torch.cuda.empty_cache()
```
- Delete tensors immediately after use
- Empty CUDA cache every 10 iterations to release fragmented memory

## Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Memory Usage | 6.8 GB (89%) | 2.6 GB (32%) | 63% reduction |
| Stability | Crashed @ 20min | Running stable | ✅ Fixed |
| Speed | 4.76 it/s | 4.71 it/s | ~1% slower (acceptable) |

## Trade-offs

1. **Slightly slower training**: Single worker vs multiple workers
   - Impact: ~1% slower (4.71 vs 4.76 it/s)
   - Benefit: 63% less memory usage

2. **Cache clearing overhead**: Every 10 iterations
   - Impact: Minimal (~0.1% overhead)
   - Benefit: Prevents memory fragmentation buildup

## Monitoring

The training monitor (`scripts/monitor_training.sh`) will alert if training crashes:
```bash
# Check alerts
tail -f /tmp/detzero_training_alert.log

# Or setup WhatsApp/Telegram alerts (see scripts/MONITORING_SETUP.md)
```

## If OOM Still Occurs

If training still crashes with OOM, try these additional steps:

### Option 1: Reduce Model Complexity
Edit `detection/tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml`:
```yaml
DENSE_HEAD:
    NUM_HM_CONV: 1  # Reduce from 2 to 1
    SHARED_CONV_CHANNEL: 32  # Reduce from 64 to 32
```

### Option 2: Gradient Checkpointing
Add to model config (requires code modification):
```python
# In model forward pass
from torch.utils.checkpoint import checkpoint
output = checkpoint(self.backbone, input)
```

### Option 3: Mixed Precision Training
Use automatic mixed precision (FP16):
```python
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    loss = model(batch)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### Option 4: Use Smaller Point Cloud Range
Edit `detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml`:
```yaml
POINT_CLOUD_RANGE: [-50, -50, -2, 50, 50, 4]  # Reduce from [-75.2, -75.2, ...]
```

## Current Training Status

Training is now running stably with:
- Memory: 2.6 GB / 8.2 GB (32% - safe margin)
- Speed: 4.71 it/s
- ETA: ~12.5 hours for 30 epochs

## Files Modified

1. `scripts/train_8k_waymo.sh` - Added CUDA allocator config, reduced workers
2. `detection/tools/train_utils.py` - Added explicit memory cleanup in training loop

## References

- [PyTorch Memory Management](https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)
- [CUDA Memory Allocator](https://pytorch.org/docs/stable/notes/cuda.html#memory-management)
