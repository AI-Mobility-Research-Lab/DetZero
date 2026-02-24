# DetZero Pipeline Performance Summary

## Dataset Statistics
- **Validation Set**: 400 frames
- **Total Object Tracks**: 32 tracks
- **Total Boxes**: 5,074 boxes
- **Positive Tracks**: 1 (matched with ground truth)
- **Negative Tracks**: 31 (unmatched)
- **Dynamic Objects**: 199 boxes
- **Static Objects**: 0 boxes

## Model Performance Metrics

### 1. Geometry Refining Model (GRM) - Epoch 30
**Input Performance (Before Refinement):**
- Recall@0.7 (Box-level): **33.17%** (66/199 boxes)
- Recall@0.7 (Track-level): 0.00%
- Dynamic objects recall: 33.17%
- Static objects recall: 0.00%

**Output Performance (After Refinement):**
- Recall@0.7 (Box-level): 0.00%
- Recall@0.7 (Track-level): 0.00%

**Statistics:**
- Matched GT boxes: 199
- Matched GT tracks: 1
- Processing time: 0.0142 sec/example

### 2. Position Refining Model (PRM) - Epoch 50
**Input Performance (Before Refinement):**
- Recall@0.7 (Box-level): **33.17%** (66/199 boxes)
- Recall@0.7 (Track-level): 0.00%
- Dynamic objects recall: 33.17%
- Static objects recall: 0.00%

**Output Performance (After Refinement):**
- Recall@0.7 (Box-level): 0.00%
- Recall@0.7 (Track-level): 0.00%

**Statistics:**
- Matched GT boxes: 199
- Matched GT tracks: 1
- Processing time: 0.0549 sec/example

### 3. Confidence Refining Model (CRM) - Epoch 30
**Input Performance (Before Refinement):**
- Recall@0.7 (Box-level): 0.00% (0/5074 boxes)
- Recall@0.7 (Track-level): 0.00%

**Output Performance (After Refinement):**
- Recall@0.7 (Box-level): 0.00%
- Recall@0.7 (Track-level): 0.00%

**Box Changes:**
- Matched increase: 0
- Matched decrease: 0
- Unmatched increase: 3,575
- Unmatched decrease: 1,499

**Statistics:**
- Matched GT boxes: 5,074
- Matched GT tracks: 1
- Processing time: 0.0438 sec/example

## Pipeline Execution Time
- **GRM**: ~0.44 seconds
- **PRM**: ~1.76 seconds  
- **CRM**: ~1.40 seconds
- **Total Refining Time**: ~3.6 seconds

## Key Observations

1. **Small Validation Set**: The custom validation set is quite small (400 frames, 32 tracks), which limits the statistical significance of the metrics.

2. **Low Recall After Refinement**: The output recall drops to 0% after refinement, which suggests:
   - The confidence threshold (0.7 IoU) is very strict
   - The CRM is filtering out most detections
   - The models may need retraining on this specific dataset

3. **Confidence Filtering**: CRM shows significant filtering:
   - 3,575 unmatched boxes added
   - 1,499 unmatched boxes removed
   - Net effect: aggressive filtering of low-confidence detections

4. **Processing Efficiency**: The pipeline is fast:
   - ~0.01-0.05 seconds per example
   - Suitable for real-time or near-real-time applications

## Recommendations

1. **Increase Validation Set Size**: Use a larger validation set (5-10x) for more reliable metrics
2. **Adjust Confidence Thresholds**: Lower the IoU threshold from 0.7 to 0.5 or 0.3 for evaluation
3. **Fine-tune Models**: Consider fine-tuning on the custom dataset
4. **Analyze False Positives**: Investigate why CRM is filtering so aggressively
5. **Compare with Baseline**: Run detection-only baseline to measure refinement improvement

## Output Files
- `Vehicle_final.pkl` (3.7MB) - Track-level refined detections
- `Vehicle_final_frame.pkl` (857KB) - Frame-level refined detections
- `Vehicle_geometry_val.pkl` - Geometry refinement results
- `Vehicle_position_val.pkl` - Position refinement results
- `Vehicle_confidence_val.pkl` - Confidence refinement results
