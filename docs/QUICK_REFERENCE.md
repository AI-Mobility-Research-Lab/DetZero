# DetZero Quick Reference Card

**Last Updated**: February 23, 2026, 20:50

---

## 🎯 Current Status

**Training in Progress**: 40% of epoch 1 complete  
**ETA**: ~15.5 hours (completion ~12:00 PM tomorrow)  
**Status**: ✅ Healthy (GPU 40% memory, 74°C, 3.74 it/s)

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Progress** | 2,908 / 7,200 iterations |
| **Speed** | 3.74 it/s |
| **Loss** | 4.7 (decreasing) |
| **GPU Memory** | 3.3 GB / 8 GB (40%) |
| **Temperature** | 74°C |
| **ETA** | ~16 hours total |

---

## 🚀 Quick Commands

### Check Training Status
```bash
cd /home/aimob/projects/DetZero
./scripts/check_training_status.sh
```

### View Live Training
```bash
tmux attach -t training
# Detach: Ctrl+B, then D
```

### Check GPU
```bash
nvidia-smi
```

### View Logs
```bash
tail -f detection/output/cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt
```

---

## 📁 Key Files

### For Sharing
- **Status Report**: `docs/PROJECT_STATUS.md` ⭐
- **Directory Structure**: `docs/DIRECTORY_STRUCTURE.md`
- **This Quick Reference**: `docs/QUICK_REFERENCE.md`

### For Monitoring
- **Status Script**: `scripts/check_training_status.sh`
- **Training Logs**: `detection/output/.../log_train_*.txt`
- **Checkpoints**: `detection/output/.../ckpt/`

---

## 🎓 What We Did

1. ✅ **Identified Problem**: Refinement producing 321% false positives
2. ✅ **Found Root Cause**: Interleaved sequences in 400-frame dataset
3. ✅ **Converted Dataset**: 8K nuScenes → DetZero format (7,200 train + 800 val)
4. ✅ **Fixed Bugs**: Data augmentation crashes with empty bounding boxes
5. 🔄 **Training Model**: CenterPoint on 8K dataset (in progress)

---

## 📈 Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Training Data** | 400 frames | 7,200 frames | 18x more |
| **Boxes/Frame** | 9.5 | 15-25 | 58-163% |
| **Tracking** | Broken | Continuous | Fixed |
| **Refinement FP** | +321% | +10-30% | 10x better |
| **CRM Score** | 0.366 | 0.7-0.9 | 2-3x better |

---

## 🔧 Technical Details

- **Model**: CenterPoint (single-stage 3D detection)
- **Dataset**: 8,000 frames (7,200 train + 800 val)
- **Batch Size**: 1 (optimized for 8GB GPU)
- **Epochs**: 30
- **GPU**: RTX 4060 (8GB)
- **Persistence**: tmux session "training"

---

## 📞 Need Help?

### Training Issues
1. Check status: `./scripts/check_training_status.sh`
2. View logs: `tail -f detection/output/.../log_train_*.txt`
3. Check GPU: `nvidia-smi`

### Resume Training (if stopped)
```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml \
    --batch_size 1 \
    --epochs 30 \
    --workers 4 \
    --extra_tag waymo_8k \
    --fix_random_seed \
    --ckpt output/.../ckpt/checkpoint_epoch_X.pth
```

---

## 📅 Timeline

**Today (Feb 23)**:
- ✅ Problem analysis
- ✅ Dataset conversion
- ✅ Bug fixes
- 🔄 Training started (20:41)

**Tomorrow (Feb 24)**:
- ⏳ Training completes (~12:00 PM)
- 📊 Model evaluation
- 🧪 Pipeline testing
- 📈 Results analysis

---

## 🎯 Next Steps

1. **Wait for training** (~15.5 hours)
2. **Evaluate model** on validation set
3. **Run full pipeline** (detection → tracking → refinement)
4. **Validate improvements** against expected metrics
5. **Share results** with team

---

**For detailed information, see**: `docs/PROJECT_STATUS.md`
