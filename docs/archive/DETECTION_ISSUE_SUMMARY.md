# Detection Issue Summary

## Problem

The pre-trained checkpoint (`checkpoint_epoch_80.pth`) was trained with a specific CenterPoint architecture (likely PillarVFE-based from nuScenes), but we're trying to use it with a different architecture (VoxelResBackBone8x from Waymo configs).

This causes architecture mismatches and spatial dimension errors.

## Root Cause

The checkpoint from OpenPCDet was trained on nuScenes format with:
- PillarVFE feature extractor
- PointPillarScatter for BEV mapping
- Specific voxel sizes and network architecture

Our converted Waymo dataset needs:
- Compatible architecture with the checkpoint
- OR a new checkpoint trained specifically for the Waymo format

## Solutions

### Option 1: Train New Model (Recommended)

Train a new CenterPoint model specifically for the converted 8K Waymo dataset:

```bash
cd detection
python tools/train.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep.yaml \
    --batch_size 8 \
    --epochs 30
```

This will:
- Use the correct architecture for Waymo format
- Train on all 7,200 training frames
- Take ~1-2 days on GPU

### Option 2: Use Existing Waymo Checkpoint

If you have a pre-trained Waymo checkpoint, use it directly:

```bash
cd detection
python tools/test.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_1sweep.yaml \
    --ckpt path/to/waymo_checkpoint.pth \
    --batch_size 1
```

### Option 3: Convert Checkpoint Architecture (Complex)

Convert the nuScenes checkpoint to Waymo architecture - requires:
- Understanding layer mappings
- Adjusting dimensions
- Testing compatibility
- Not recommended due to complexity

## Why This Happened

The conversion process successfully converted the **data format** from nuScenes to Waymo, but the **model checkpoint** is still trained for nuScenes architecture. The model architecture and checkpoint must match.

## Recommended Path Forward

1. **Train a new model** on the converted 8K Waymo dataset using `centerpoint_1sweep.yaml`
2. This gives you a properly trained model for your data format
3. Then run tracking and refinement on the new detections

## Alternative: Use Original nuScenes Pipeline

If training time is a concern, you could:
1. Use the OpenPCDet nuScenes pipeline directly for detection
2. Convert only the detection results to Waymo format
3. Run tracking and refinement on converted results

This avoids retraining but keeps the format conversion issue in the pipeline.

## Files Status

- ✅ Data conversion: Complete and validated (8,000 frames)
- ✅ Dataset loading: Works with DetZero
- ❌ Model checkpoint: Architecture mismatch
- ⏳ Detection: Needs compatible checkpoint

## Next Steps

Choose one of the options above based on your timeline and resources. Training a new model is the cleanest solution and will give you the best results for the full pipeline (detection → tracking → refinement).
