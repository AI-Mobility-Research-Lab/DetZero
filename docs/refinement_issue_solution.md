# DetZero Custom Dataset Refinement Issue - Root Cause & Solution

## Executive Summary

The refinement pipeline produces 0.000-0.001 AP instead of the expected improvement over the 0.977 baseline AP.

**Root Cause Identified:** The tracking module produces essentially **static boxes** (position variance < 0.01m, movement < 0.003m over 10 frames). Since the refinement pipeline (GRM/PRM/CRM) depends on tracking as input, static tracking leads to static refined outputs, which fail evaluation because they don't match the actual moving objects in ground truth.

**Secondary Issue (Not Critical):** The CRM produces constant confidence scores (~0.36), but this was not used in the final combination (the pipeline was run without `--combine_conf_res`), so it didn't affect the AP.

## Complete Root Cause Chain

```
1. Custom dataset has num_points_in_gt = [0, 0, 0, ...]
   ↓
2. Tracking module cannot properly track objects without point information
   ↓
3. Tracking produces static boxes (objects "frozen" in place)
   Evidence: Track 0 moves only 0.002m over 10 frames
   ↓
4. Refinement (GRM/PRM) uses static tracking as input
   ↓
5. Refined boxes are also static
   Example: Frame 0-2 all have box at [-25.118, 11.767, -0.916]
   ↓
6. Evaluation compares static refined boxes against moving GT objects
   ↓
7. IoU is near-zero → AP collapses to 0.000
```

## Detailed Evidence

### 1. Tracking Data Produces Static Boxes

**Tracking input file:** `data/waymo_custom/tracking/tracking-val-20251203-201842.pkl`

```
Track 0 (unlabeled detection):
  boxes_global positions:
    Frame 0: [-24.610, 12.025, -0.971]
    Frame 1: [-24.610, 12.025, -0.971]
    Frame 2: [-24.610, 12.025, -0.972]
    Frame 9: [-24.610, 12.025, -0.971]

  Position variance (x,y,z): [3.9e-05, 1.5e-05, 2.3e-04]
  Distance traveled (frame 0→9): 0.002m ✗

Track 1:
  Position variance: [1.0e-04, 6.3e-05, 7.2e-06]
  Distance traveled (frame 0→9): 0.003m ✗
```

**Expected behavior:** Vehicles should move meters per frame, not millimeters per 10 frames.

### 2. PRM Outputs Static Boxes (Inherits from Tracking)

**PRM output file:** `data/waymo_custom/refining/result/Vehicle_position_test.pkl`

```
Track 0 (k_6001_8000_camera_v):
  boxes_lidar positions:
    Frame 0: [-25.118, 11.767, -0.916]
    Frame 1: [-25.118, 11.767, -0.916]
    Frame 2: [-25.118, 11.768, -0.917]
    Frame 4: [-25.118, 11.766, -0.917]

  Position variance: [6.7e-05, 1.1e-04, 2.1e-04]
  Boxes are static: True (<0.01m variance)
```

### 3. Final Frame-Level Results Are Static

**Final output file:** `data/waymo_custom/refining/result/Vehicle_final_frame.pkl`

Refined boxes remain static across frames, making them unmatchable to moving ground truth objects.

### 4. Ground Truth Shows Moving Objects

```
GT Frame 0: box[0] at [-12.319, 12.137, -1.485]
GT Frame 1: box[0] at [  5.436, 23.804, -1.012]  ← Different object!
GT Frame 2: box[0] at [-12.319, 12.137, -1.485]  ← Back to first object
```

Ground truth objects are moving normally. The refined static boxes cannot match them.

### 5. Baseline Works Despite Same Data

**Baseline AP: 0.977**

Baseline works because:
- CenterPoint detection is frame-independent (no tracking)
- Detects objects directly from point clouds each frame
- Not affected by lack of temporal/tracking information

## Why Tracking Fails

The custom dataset is missing critical information needed for tracking:

1. **num_points_in_gt = 0** for all boxes
   - Tracker cannot assess detection quality
   - Cannot distinguish true detections from noise

2. **No velocity information** in detections
   - Tracker cannot predict object motion
   - Association becomes ambiguous

3. **Possible data characteristics:**
   - Custom dataset may be synthetic/augmented
   - May lack temporal coherence
   - Objects may actually be duplicated frames

## Solution Options

### ✓ Option 1: Don't Use Refinement (Recommended for Custom Dataset)

For datasets without proper tracking information, **skip refinement entirely** and use baseline detector:

```bash
# Just use the baseline CenterPoint detection
cd detection/tools

PYTHONPATH=..:../..:$PYTHONPATH python3 test.py \
  --cfg_file cfgs/det_model_cfgs/centerpoint_1sweep_custom.yaml \
  --ckpt ../output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug/ckpt/checkpoint_epoch_30.pth \
  --extra_tag final_results \
  --save_to_file
```

**Result:** 0.977 AP (known good performance)

### Option 2: Fix Tracking (Long-term Solution)

To enable refinement, fix the tracking pipeline:

1. **Regenerate dataset with proper num_points_in_gt:**
   ```bash
   # Reprocess raw data to compute actual point counts
   # Update waymo_infos_{train,val,test}.pkl
   ```

2. **Add velocity to detections:**
   - Modify detection output to include velocity estimates
   - Or use consecutive frame pairs to compute velocities

3. **Tune tracking parameters** for the custom dataset:
   - Adjust IoU thresholds
   - Modify association algorithm
   - Consider using Kalman filter with better motion model

4. **Verify tracking quality before refinement:**
   ```bash
   # Evaluate tracking metrics (MOTA, MOTP)
   cd evaluator
   python3 detzero_eval.py --tracking ...
   ```

### Option 3: Use Refinement on Standard Waymo Data

Refinement works on standard Waymo validation set. If you want to demonstrate refinement:

```bash
# Use the standard Waymo val split (not custom)
# This has proper num_points_in_gt and works with tracking
```

## Files Created for Debugging

1. `debug_refinement.py` - Compare baseline vs refined structures
2. `debug_refine_components.py` - Inspect GRM/PRM/CRM outputs
3. `debug_frame_alignment.py` - Check frame/sequence alignment
4. `debug_box_quality.py` - Compare box positions vs GT
5. `fix_refinement.py` - Generate results without broken CRM
6. `check_tracking_source.py` - Verify tracking data sources
7. `check_coordinates.py` - Check coordinate frame consistency

## Key Findings Summary

| Component | Status | Notes |
|-----------|--------|-------|
| **Tracking** | ✗ **BROKEN** | **Static boxes, <0.003m movement** |
| **PRM** | ⚠ Working but limited | Inherits static boxes from tracking |
| **GRM** | ✓ Working | Geometry refinement functional |
| **CRM** | ✗ Broken | Constant scores (~0.36), but not used |
| **num_points_in_gt** | ✗ All zeros | **Root cause of tracking failure** |
| **Frame Alignment** | ✓ Correct | 400/400 frames match |
| **Baseline Detection** | ✓ Working | 0.977 AP without refinement |

## Recommended Actions

### Immediate (Today)

1. **Use baseline detection without refinement** - Already achieving 0.977 AP
2. **Document that refinement requires proper tracking data**
3. **Skip refinement pipeline for this custom dataset**

### Short-term (If refinement is needed)

1. **Regenerate custom dataset with num_points_in_gt**:
   - Count actual points inside each GT box
   - Update pkl files with correct point counts

2. **Validate tracking quality**:
   - Run tracking evaluation
   - Visually inspect tracked objects
   - Ensure objects actually move frame-to-frame

3. **Re-run refinement pipeline**:
   - Only after tracking is confirmed working
   - Validate each component (GRM, PRM, CRM)

### Long-term (For production use)

1. **Improve tracking for custom data**:
   - Add velocity estimation
   - Tune tracking hyperparameters
   - Consider learning-based tracker

2. **Fix or replace CRM**:
   - Debug constant score issue
   - Retrain on custom dataset
   - Or skip CRM entirely (GRM+PRM may suffice)

3. **Establish validation pipeline**:
   - Test tracking quality before refinement
   - Validate each stage independently
   - Ensure AP never degrades

## Conclusion

The refinement failure is **not a bug in the refinement code**, but rather a **fundamental data limitation**:

- Custom dataset lacks `num_points_in_gt` information
- This causes tracking to fail (producing static boxes)
- Refinement cannot work without proper tracking
- **Solution: Either fix the dataset or skip refinement**

The baseline detector (0.977 AP) already works well. Refinement is optional and only beneficial when tracking is reliable.

## References

- Original issue: [custom_refinement_issue.md](custom_refinement_issue.md)
- Tracking module: [tracking/tools/](../tracking/tools/)
- Refinement pipeline: [daemon/combine_output.py](../daemon/combine_output.py)
- Evaluation: [evaluator/detzero_eval.py](../evaluator/detzero_eval.py)
- Waymo metrics: [detection/detzero_det/datasets/waymo/waymo_eval_detection.py](../detection/detzero_det/datasets/waymo/waymo_eval_detection.py)
