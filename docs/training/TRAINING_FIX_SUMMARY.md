# Training Fix Summary

## Problem
Training crashed at iteration ~625 with IndexError:
```
IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed
```

The error occurred in data augmentation when trying to flip empty gt_boxes arrays. Some frames in the dataset have no objects, resulting in empty gt_boxes arrays with shape `[0, 9]`. However, the augmentation code didn't handle empty arrays properly.

## Root Cause
The augmentation functions in `detection/detzero_det/datasets/augmentor/augmentor_utils.py` attempted to index empty gt_boxes arrays without checking if they were empty first:

```python
# This fails when gt_boxes is empty [0, 9]
gt_boxes[:, 1] = -gt_boxes[:, 1]
```

## Solution
Added empty array checks to all augmentation functions:

### Fixed Functions
1. `random_flip_along_x()` - Added `if len(gt_boxes) > 0:` check
2. `random_flip_along_y()` - Added `if len(gt_boxes) > 0:` check  
3. `global_rotation()` - Added `if len(gt_boxes) > 0:` check
4. `global_scaling()` - Added `if len(gt_boxes) > 0:` check
5. `global_translation()` - Added `if len(gt_boxes) > 0:` check

### Example Fix
```python
def random_flip_along_x(gt_boxes, points, return_enable_xy=False):
    enable = np.random.choice([False, True], replace=False, p=[0.5, 0.5])
    if enable:
        # Handle empty gt_boxes (shape [0, 9] or [0])
        if len(gt_boxes) > 0:
            gt_boxes[:, 1] = -gt_boxes[:, 1]
            gt_boxes[:, 6] = -gt_boxes[:, 6]
            if gt_boxes.shape[1] > 7:
                gt_boxes[:, 8] = -gt_boxes[:, 8]
        points[:, 1] = -points[:, 1]
    return gt_boxes, points
```

## Verification
Created test script `scripts/test_augmentor_fix.py` that verifies all augmentation functions handle empty gt_boxes correctly. All tests passed:

```
✅ random_flip_along_x: PASSED
✅ random_flip_along_y: PASSED
✅ global_rotation: PASSED
✅ global_scaling: PASSED
✅ global_translation: PASSED
```

## Training Status
- **Status**: Running successfully
- **Current Progress**: Iteration 631+ (passed the crash point at 625)
- **Loss**: Decreasing from 28.5 → 5-6
- **Speed**: ~2.2 iterations/second
- **ETA**: See below

## Training Timeline

### Per Epoch
- Iterations per epoch: 3,600 (7,200 train samples / batch_size 8 / 4 workers)
- Time per epoch: ~27 minutes (3,600 iterations / 2.2 it/s = 1,636 seconds)

### Full Training (30 epochs)
- Total iterations: 108,000
- Total time: ~13.5 hours (30 epochs × 27 minutes)
- Expected completion: ~14 hours from start (accounting for validation)

### Current Progress
- Epoch 1: In progress (17% complete at iteration 631/3,600)
- Estimated epoch 1 completion: ~20 more minutes
- Estimated full training completion: ~13 hours remaining

## Files Modified
- `detection/detzero_det/datasets/augmentor/augmentor_utils.py` - Fixed 5 augmentation functions

## Files Created
- `scripts/test_augmentor_fix.py` - Test script for augmentation fixes
- `scripts/verify_gt_boxes_fix.py` - Script to verify gt_boxes shapes in dataset
- `scripts/check_pkl_structure.py` - Script to inspect pkl file structure
- `scripts/check_annos_structure.py` - Script to inspect annotations structure
- `scripts/fix_empty_gt_boxes.py` - Script to fix empty gt_boxes (not needed, data was correct)
- `TRAINING_FIX_SUMMARY.md` - This file

## Next Steps
1. ✅ Training is running successfully
2. ⏳ Wait for training to complete (~13 hours)
3. Test the trained model on validation set
4. Run full pipeline: detection → tracking → refinement
5. Compare results with ablation study

## Expected Improvements
After training completes, we expect:
- Detection: 15-25 boxes/frame (vs 9.5 with old model)
- Tracking: Continuous trajectories (vs broken with interleaved sequences)
- Refinement: +10-30% boxes (vs +321% false positives)
- CRM scores: 0.7-0.9 (vs 0.366)

---

**Training is now running smoothly! The fix successfully handles empty gt_boxes in data augmentation.**
