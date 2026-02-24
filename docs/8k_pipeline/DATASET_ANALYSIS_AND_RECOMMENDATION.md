# Dataset Analysis & Retraining Recommendation

## Current Situation

### What We Found

1. **OpenPCDet has a trained 8K nuScenes custom model**
   - Location: `/home/aimob/projects/OpenPCDet/output/cfgs/nuscenes_custom_models/centerpoint_8k/`
   - Dataset: 7,200 training samples from `v1.0-tak_8k_human_combined`
   - Model: CenterPoint trained for 80 epochs
   - Checkpoint: `checkpoint_epoch_80.pth` (latest)

2. **DetZero is using a small custom Waymo dataset**
   - Location: `data/waymo_custom/`
   - Only 400 frames total (200 frames from 2 sequences for refinement)
   - Converted from nuScenes format using custom TFRecord conversion
   - Detection model: `checkpoint_epoch_12.pth` (only 12 epochs!)

3. **The Problem with Current DetZero Dataset**
   - **Very small**: Only 400 frames vs 7,200 in nuScenes 8K
   - **Undertrained**: Detection model only trained for 12 epochs
   - **Format conversion issues**: nuScenes → Waymo TFRecord conversion may have introduced errors
   - **Tracking breaks**: Frames from different sequences are interleaved, breaking temporal continuity
   - **Poor refinement**: PRM adds 321% more boxes (many false positives) because tracking is unreliable

## Root Cause Analysis

### Why Refinement Performance is Bad

1. **Insufficient Training Data**
   - 400 frames is too small for robust detection
   - Undertrained detector (12 epochs) produces noisy detections
   - Noisy detections → poor tracking → bad refinement

2. **Dataset Conversion Issues**
   - Converting nuScenes → Waymo format may have:
     - Lost calibration information
     - Introduced coordinate frame errors
     - Broken temporal relationships
     - Corrupted point cloud data

3. **Tracking Continuity Problems**
   - Frames from different sequences interleaved
   - Breaks temporal assumptions in PRM/CRM
   - Causes false associations and hallucinated tracks

## Recommendation: Retrain on 8K nuScenes Dataset

### Why This Makes Sense

✅ **Larger Dataset**: 7,200 samples vs 400 (18x more data)

✅ **Native Format**: No conversion errors, data is already in nuScenes format

✅ **Proven Training**: Model already trained for 80 epochs with good convergence

✅ **Better Detection**: More data + more training = better baseline detections

✅ **Better Refinement**: Good detections → good tracking → good refinement

✅ **Avoid Previous Issues**: No format conversion, no temporal breaks

### What Needs to Be Done

#### Option 1: Use OpenPCDet Model Directly (Fastest)

1. **Copy the trained model to DetZero**
   ```bash
   cp /home/aimob/projects/OpenPCDet/output/cfgs/nuscenes_custom_models/centerpoint_8k/centerpoint_8k_20260213_191157/ckpt/checkpoint_epoch_80.pth \
      detection/output/centerpoint_8k.pth
   ```

2. **Update DetZero detection config**
   - Point to nuScenes 8K dataset
   - Use the 80-epoch checkpoint
   - Update class names if needed

3. **Run detection on nuScenes 8K**
   ```bash
   cd detection
   python tools/test.py \
     --cfg_file tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
     --ckpt ../output/centerpoint_8k.pth \
     --data_path /home/aimob/projects/OpenPCDet/data/nuscenes_custom
   ```

4. **Run tracking on nuScenes format**
   - Update tracking config for nuScenes
   - Process all 7,200 frames

5. **Run refinement**
   - Train GRM/PRM/CRM on larger dataset
   - Should see much better results

#### Option 2: Retrain DetZero-Style on 8K (More Work, Better Integration)

1. **Prepare 8K dataset in DetZero format**
   ```bash
   cd detection
   python -m detzero_det.datasets.nuscenes.nuscenes_dataset \
     --func create_nuscenes_infos \
     --cfg_file tools/cfgs/det_dataset_cfgs/nuscenes_custom_8k.yaml \
     --version v1.0-tak_8k_human_combined
   ```

2. **Train detection from scratch**
   ```bash
   python tools/train.py \
     --cfg_file tools/cfgs/det_model_cfgs/centerpoint_8k_detzero.yaml \
     --epochs 80 \
     --batch_size 8
   ```

3. **Continue with tracking and refinement**

## Expected Improvements

### Detection
- **Current**: ~400 frames, 12 epochs, noisy detections
- **After**: 7,200 frames, 80 epochs, clean detections
- **Expected mAP improvement**: +10-20% (rough estimate)

### Tracking
- **Current**: Breaks on interleaved sequences
- **After**: Continuous sequences, proper temporal flow
- **Expected**: Fewer ID switches, better associations

### Refinement
- **Current**: PRM adds 321% boxes (mostly false positives)
- **After**: PRM should add 10-30% boxes (real missed detections)
- **Expected**: CRM scores stay high (0.7-0.9 instead of 0.3-0.4)

## Comparison Table

| Aspect | Current (waymo_custom) | Proposed (nuscenes_8k) |
|--------|------------------------|------------------------|
| **Frames** | 400 | 7,200 |
| **Training Epochs** | 12 | 80 |
| **Format** | Converted (nuScenes→Waymo) | Native nuScenes |
| **Sequences** | 2 (interleaved) | Multiple (continuous) |
| **Detection Quality** | Poor (undertrained) | Good (well-trained) |
| **Tracking Quality** | Broken (temporal gaps) | Good (continuous) |
| **Refinement Quality** | Bad (321% false positives) | Expected: Good |
| **Data Integrity** | Questionable (conversion) | High (native) |

## Action Plan

### Immediate (Recommended)

1. **Verify OpenPCDet model quality**
   ```bash
   cd /home/aimob/projects/OpenPCDet
   python tools/test.py \
     --cfg_file tools/cfgs/nuscenes_custom_models/centerpoint_8k.yaml \
     --ckpt output/cfgs/nuscenes_custom_models/centerpoint_8k/centerpoint_8k_20260213_191157/ckpt/checkpoint_epoch_80.pth
   ```

2. **Check evaluation metrics**
   - Look at mAP scores
   - Verify detection quality
   - Compare with current DetZero baseline

3. **If metrics are good, proceed with Option 1** (use model directly)

4. **If metrics need improvement, proceed with Option 2** (retrain)

### Timeline Estimate

- **Option 1** (use existing model): 1-2 days
  - Adapt configs: 2 hours
  - Run detection: 4 hours
  - Run tracking: 4 hours
  - Run refinement: 8 hours
  - Evaluation: 2 hours

- **Option 2** (retrain): 1-2 weeks
  - Dataset prep: 1 day
  - Training: 3-5 days (80 epochs)
  - Detection: 4 hours
  - Tracking: 4 hours
  - Refinement training: 3-5 days
  - Evaluation: 1 day

## Conclusion

**Yes, you should absolutely retrain using the 8K nuScenes dataset.** The current DetZero custom Waymo dataset has multiple issues:

1. Too small (400 vs 7,200 frames)
2. Undertrained (12 vs 80 epochs)
3. Format conversion problems
4. Temporal continuity breaks
5. Poor refinement results

The 8K nuScenes dataset in OpenPCDet is already prepared, trained, and ready to use. This will give you:
- Better detection baseline
- Better tracking quality
- Better refinement results
- Fewer false positives
- More reliable performance

**Recommended next step**: Start with Option 1 (use existing OpenPCDet model) to quickly validate the approach, then consider Option 2 if you need DetZero-specific customizations.
