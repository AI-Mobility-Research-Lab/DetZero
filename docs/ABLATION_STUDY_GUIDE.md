# DetZero Ablation Study Guide

## Purpose

Separate and visualize the effects of each refinement module (GRM, PRM, CRM) to identify which ones improve results and which ones generate false positives.

## Quick Start

### Step 1: Generate Ablation Data

```bash
python generate_ablation_data.py
```

This creates 4 variants:
- `detection`: Baseline detection only
- `grm`: Detection + GRM (geometry refinement)
- `grm_prm`: Detection + GRM + PRM (geometry + position)
- `grm_prm_crm`: Full pipeline (geometry + position + confidence)

### Step 2: Prepare Visualization Data

```bash
python prepare_ablation_viz.py
```

This converts the data to JSON format and generates statistics showing:
- How many boxes each module adds
- Average confidence scores
- Per-frame box counts

### Step 3: View Results

Open in browser:
```
http://localhost:8000/ablation.html
```

## What to Look For

### Good Signs
- ✅ Boxes align with actual objects
- ✅ Consistent tracking across frames
- ✅ High confidence scores (>0.7)
- ✅ Reasonable box dimensions

### Bad Signs (False Positives)
- ❌ Boxes in empty space
- ❌ Flickering boxes (appear/disappear)
- ❌ Very low confidence scores (<0.5)
- ❌ Unrealistic dimensions

## Analysis Questions

1. **Does GRM help?**
   - Compare top-left (detection) vs top-right (+ GRM)
   - Does it fix box dimensions?
   - Does it add false positives?

2. **Does PRM help?**
   - Compare top-right (+ GRM) vs bottom-left (+ GRM + PRM)
   - Does it improve box positions?
   - Does it add many new boxes? Are they real?

3. **Does CRM help?**
   - Compare bottom-left (+ GRM + PRM) vs bottom-right (full)
   - Does it filter out false positives?
   - Or does it keep/add more false positives?

## Expected Insights

Based on your observation that refinement adds "a lot of extra boxes that don't look real":

### Hypothesis 1: PRM is the problem
- If bottom-left panel shows many false positives
- PRM might be hallucinating objects from tracking

### Hypothesis 2: CRM is the problem
- If bottom-right has more boxes than bottom-left
- CRM might be boosting confidence of false positives

### Hypothesis 3: GRM is fine
- If top-right looks similar to top-left
- GRM probably just adjusts dimensions, doesn't add boxes

## Recommended Actions

### If GRM is good but PRM/CRM are bad:
```bash
# Use only detection + GRM
python fix_refinement.py --use-only grm
```

### If GRM+PRM are good but CRM is bad:
```bash
# Use detection + GRM + PRM (skip CRM)
python fix_refinement.py --skip-crm
```

### If only detection is reliable:
```bash
# Use detection only, skip all refinement
# Just use the original detection results
```

## Quantitative Analysis

After viewing, you can also run evaluation on each variant:

```bash
cd evaluator

# Evaluate detection only
PYTHONPATH=..:$PYTHONPATH python3 detzero_eval.py \
  --det_result_path ../data/waymo_custom/ablation/Vehicle_detection_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle --evaluate_metrics object

# Evaluate + GRM
PYTHONPATH=..:$PYTHONPATH python3 detzero_eval.py \
  --det_result_path ../data/waymo_custom/ablation/Vehicle_grm_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle --evaluate_metrics object

# Evaluate + GRM + PRM
PYTHONPATH=..:$PYTHONPATH python3 detzero_eval.py \
  --det_result_path ../data/waymo_custom/ablation/Vehicle_grm_prm_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle --evaluate_metrics object

# Evaluate full pipeline
PYTHONPATH=..:$PYTHONPATH python3 detzero_eval.py \
  --det_result_path ../data/waymo_custom/ablation/Vehicle_grm_prm_crm_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle --evaluate_metrics object
```

This will give you mAP scores for each variant to see which actually improves performance.

## Files Created

```
data/waymo_custom/ablation/
├── Vehicle_detection_test.pkl      # Baseline
├── Vehicle_grm_test.pkl            # + GRM
├── Vehicle_grm_prm_test.pkl        # + GRM + PRM
└── Vehicle_grm_prm_crm_test.pkl    # Full pipeline

web_visualizer/data/ablation/
├── detection_data.json
├── grm_data.json
├── grm_prm_data.json
├── grm_prm_crm_data.json
└── ablation_summary.json
```

## Tips

- Use the frame slider to find frames with obvious false positives
- Use the play button to see temporal consistency
- Click "Reset View" to sync all 4 camera angles
- Look for patterns: do false positives appear in specific areas?

## Next Steps

Once you identify which modules work well:
1. Modify the pipeline to use only the good modules
2. Re-evaluate on the full test set
3. Compare mAP scores to confirm improvement
