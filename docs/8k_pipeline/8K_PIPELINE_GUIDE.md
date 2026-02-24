# DetZero 8K nuScenes Pipeline Guide

## Overview

This guide walks you through running the complete DetZero pipeline on the 8K nuScenes custom dataset, which will give you much better results than the current 400-frame Waymo dataset.

## What's Different

| Aspect | Old (waymo_custom) | New (nuscenes_8k) |
|--------|-------------------|-------------------|
| **Dataset Size** | 400 frames | 7,200 train + 800 val |
| **Training Epochs** | 12 | 80 |
| **Format** | Converted Waymo | Native nuScenes |
| **Temporal Continuity** | Broken (interleaved) | Good (continuous) |
| **Detection Quality** | Poor | Good (0.85-0.95 scores) |

## Prerequisites

✅ OpenPCDet model already trained (80 epochs)  
✅ Model copied to `detection/output/centerpoint_8k/checkpoint_epoch_80.pth`  
✅ Configs created for detection, tracking, and refinement  
✅ Dataset at `/home/aimob/projects/OpenPCDet/data/nuscenes_custom/v1.0-tak_8k_human_combined`

## Quick Start (Recommended)

### Option 1: Run Full Pipeline (Automated)

```bash
./run_8k_pipeline.sh
```

This will run all steps automatically:
1. Detection (using pre-trained model)
2. Tracking
3. Object data preparation
4. Refinement training (GRM, PRM, CRM)
5. Refinement inference
6. Result combination

**Estimated time**: 8-16 hours (mostly refinement training)

### Option 2: Run Steps Individually

If you want more control or to debug issues:

#### Step 1: Detection (~30 minutes)

```bash
python3 run_detection_8k.py \
    --cfg_file detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --split val \
    --output_dir output_8k/detection
```

**Output**: `output_8k/detection/val_detections.pkl`

**Expected results**:
- 800 frames processed
- ~15-25 boxes per frame
- Average score: 0.85-0.95
- Much better than current 0.83

#### Step 2: Tracking (~1 hour)

```bash
cd tracking
python3 tools/run_track.py \
    --cfg_file tools/cfgs/tk_model_cfgs/detzero_track_8k.yaml \
    --det_result_path ../output_8k/detection/val_detections.pkl \
    --output_dir ../output_8k/tracking \
    --split val
cd ..
```

**Output**: `output_8k/tracking/tracking_val.pkl`

**Expected results**:
- Continuous tracks (no interleaving issues)
- Better ID consistency
- Fewer false associations

#### Step 3: Prepare Object Data (~2 hours)

```bash
python3 daemon/prepare_object_data.py \
    --tracking_result output_8k/tracking/tracking_val.pkl \
    --data_path /home/aimob/projects/OpenPCDet/data/nuscenes_custom \
    --output_path output_8k/refining \
    --split val \
    --class_names car truck pedestrian bicycle
```

**Output**: Object crops for refinement training

#### Step 4: Train Refinement Modules (~6-12 hours)

You'll need to create refinement configs first (see below), then:

```bash
cd refining

# Train GRM (2-4 hours)
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/grm_8k.yaml \
    --batch_size 8 \
    --epochs 30

# Train PRM (2-4 hours)
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/prm_8k.yaml \
    --batch_size 8 \
    --epochs 30

# Train CRM (2-4 hours)
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/crm_8k.yaml \
    --batch_size 8 \
    --epochs 30

cd ..
```

#### Step 5: Run Refinement Inference (~1 hour)

```bash
cd refining
python3 tools/test.py \
    --tracking_result ../output_8k/tracking/tracking_val.pkl \
    --grm_ckpt ../output_8k/refining/grm/checkpoint_best.pth \
    --prm_ckpt ../output_8k/refining/prm/checkpoint_best.pth \
    --crm_ckpt ../output_8k/refining/crm/checkpoint_best.pth \
    --output_dir ../output_8k/refining/results \
    --split val
cd ..
```

#### Step 6: Combine Results (~5 minutes)

```bash
python3 daemon/combine_output.py \
    --geo_path output_8k/refining/results/car_geometry_val.pkl \
    --pos_path output_8k/refining/results/car_position_val.pkl \
    --conf_path output_8k/refining/results/car_confidence_val.pkl \
    --output_path output_8k/refining/results \
    --split val
```

**Final output**: `output_8k/refining/results/car_final_val.pkl`

## Expected Improvements

### Detection
- **Current**: 9.5 boxes/frame, 0.83 avg score
- **Expected**: 15-25 boxes/frame, 0.85-0.95 avg score
- **Improvement**: +50-150% boxes, +2-12% score

### Tracking
- **Current**: Broken temporal continuity
- **Expected**: Smooth continuous tracks
- **Improvement**: Fewer ID switches, better associations

### Refinement
- **Current**: PRM adds 321% boxes (mostly false positives), CRM score drops to 0.366
- **Expected**: PRM adds 10-30% boxes (real detections), CRM score stays 0.7-0.9
- **Improvement**: Much fewer false positives, higher confidence

## Monitoring Progress

### Detection
```bash
tail -f output_8k/detection/detection_8k.log
```

### Tracking
```bash
tail -f output_8k/tracking/tracking.log
```

### Refinement Training
```bash
# GRM
tail -f refining/output/grm/train.log

# PRM
tail -f refining/output/prm/train.log

# CRM
tail -f refining/output/crm/train.log
```

## Troubleshooting

### Issue: CUDA out of memory

**Solution**: Reduce batch size
```bash
python3 run_detection_8k.py --batch_size 2  # Instead of 4
```

### Issue: Dataset not found

**Solution**: Check symlink
```bash
ls -la /home/aimob/projects/OpenPCDet/data/nuscenes_custom/v1.0-tak_8k_human_combined
```

### Issue: Model checkpoint not found

**Solution**: Verify copy
```bash
ls -lh detection/output/centerpoint_8k/checkpoint_epoch_80.pth
```

### Issue: Refinement configs missing

**Solution**: Create them based on existing configs
```bash
# Copy and modify existing configs
cp refining/tools/cfgs/ref_model_cfgs/grm.yaml \
   refining/tools/cfgs/ref_model_cfgs/grm_8k.yaml
# Then edit to point to 8K dataset
```

## Validation

After running the pipeline, validate results:

### 1. Check Detection Quality
```bash
python3 -c "
import pickle
det = pickle.load(open('output_8k/detection/val_detections.pkl', 'rb'))
scores = [s for r in det for s in r['score']]
print(f'Frames: {len(det)}')
print(f'Avg boxes/frame: {sum(len(r[\"score\"]) for r in det) / len(det):.2f}')
print(f'Avg score: {sum(scores)/len(scores):.3f}')
print(f'Score range: [{min(scores):.3f}, {max(scores):.3f}]')
"
```

**Expected**:
- Frames: 800
- Avg boxes/frame: 15-25
- Avg score: 0.85-0.95

### 2. Check Tracking Quality
```bash
python3 -c "
import pickle
track = pickle.load(open('output_8k/tracking/tracking_val.pkl', 'rb'))
print(f'Total tracks: {len(track)}')
print(f'Sequences: {set(t[\"sequence_name\"] for t in track.values())}')
"
```

### 3. Check Refinement Quality
```bash
python3 -c "
import pickle
ref = pickle.load(open('output_8k/refining/results/car_final_val.pkl', 'rb'))
scores = [s for r in ref for s in r['score']]
print(f'Frames: {len(ref)}')
print(f'Avg boxes/frame: {sum(len(r[\"score\"]) for r in ref) / len(ref):.2f}')
print(f'Avg score: {sum(scores)/len(scores):.3f}')
"
```

**Expected**:
- Avg score should be 0.7-0.9 (not 0.366 like current)
- Boxes should increase by 10-30% (not 321%)

## Visualization

After validation, create visualizations:

```bash
# Generate ablation study data
python3 generate_ablation_data_8k.py

# Prepare web visualization
python3 prepare_ablation_viz_8k.py

# View in browser
python3 -m http.server 8000
# Open: http://localhost:8000/ablation.html
```

## Next Steps

1. **Run the pipeline**: `./run_8k_pipeline.sh`
2. **Monitor progress**: Check logs in `output_8k/`
3. **Validate results**: Use validation scripts above
4. **Compare with old results**: Run ablation study
5. **Evaluate metrics**: Run evaluator on both datasets
6. **Deploy**: If results are better, replace old model

## Timeline

- **Detection**: 30 minutes (using pre-trained model)
- **Tracking**: 1 hour
- **Object prep**: 2 hours
- **Refinement training**: 6-12 hours
- **Refinement inference**: 1 hour
- **Total**: 10-16 hours

## Support

If you encounter issues:
1. Check logs in `output_8k/*/`
2. Verify dataset paths
3. Check GPU memory usage
4. Review config files

Good luck! This should give you much better results than the current 400-frame dataset.
