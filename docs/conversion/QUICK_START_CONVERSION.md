# Quick Start: Convert 8K nuScenes to DetZero Format

## TL;DR

```bash
# Run the conversion (takes ~30-60 minutes)
./scripts/run_conversion.sh --workers 8

# Validate the output
./scripts/run_conversion.sh --validate-only --output ./data/waymo_8k

# Use with DetZero detection
cd detection
python tools/test.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt output/centerpoint_8k/checkpoint_epoch_80.pth \
    --data_path ../data/waymo_8k
```

## What This Does

Converts 8,000 frames (7,200 train + 800 val) from OpenPCDet nuScenes format to DetZero Waymo format:

- ✅ Preserves all annotations (boxes, classes, velocities, track IDs)
- ✅ Converts point clouds to .npy format
- ✅ Groups frames into sequences for tracking
- ✅ Maps classes (car→Vehicle, pedestrian→Pedestrian, bicycle→Cyclist)
- ✅ Creates DetZero-compatible directory structure

## Why This Matters

Your current 400-frame dataset has issues:
- Too small (400 vs 8,000 frames)
- Undertrained (12 vs 80 epochs)
- Broken tracking (interleaved sequences)
- Poor refinement (+321% false positives)

The 8K conversion fixes all of these issues.

## Monitor Progress

Watch the logs in real-time:
```bash
tail -f logs/conversion_*.log
```

## Troubleshooting

**Out of memory?**
```bash
./scripts/run_conversion.sh --workers 2
```

**Need to resume?**
The conversion is idempotent - just run it again.

**Validation fails?**
Check the validation report for specific errors.

## Next Steps After Conversion

1. Run detection on 8K dataset
2. Run tracking (will work better with continuous sequences)
3. Run refinement (expect +10-30% boxes instead of +321%)
4. Compare results with ablation study

See `CONVERSION_IMPLEMENTATION_SUMMARY.md` for full details.
