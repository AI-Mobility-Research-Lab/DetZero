# Quick Guide: Evaluating DetZero CenterPoint in OpenPCDet

## Setup Complete

I've created the necessary configuration files for you:

### 1. Dataset Config
**Location:** `/home/aimob/projects/OpenPCDet/tools/cfgs/dataset_configs/waymo_custom_detzero.yaml`

Key settings (matching DetZero):
- `DATA_PATH: 'data/waymo_custom'`
- `POINT_CLOUD_RANGE: [-75.2, -75.2, -2, 75.2, 75.2, 4]`
- `VOXEL_SIZE: [0.1, 0.1, 0.15]`
- Point features: x, y, z, intensity, elongation

### 2. Model Config
**Location:** `/home/aimob/projects/OpenPCDet/tools/cfgs/waymo_models/centerpoint_detzero.yaml`

Architecture (matching DetZero exactly):
- VFE: MeanVFE (not PillarVFE)
- 3D Backbone: VoxelResBackBone8x
- MAP_TO_BEV: HeightCompression
- 2D Backbone: 2 layers [128, 256]
- Dense Head: CenterHead with IOU prediction
- FEATURE_MAP_STRIDE: 8

## Installation Status

Currently installing OpenPCDet with:
```bash
cd /home/aimob/projects/OpenPCDet
pip install -e . --user
```

## Once Installation Completes

### Run Evaluation

```bash
cd /home/aimob/projects/OpenPCDet

python tools/test.py \
  --cfg_file tools/cfgs/waymo_models/centerpoint_detzero.yaml \
  --ckpt /home/aimob/projects/DetZero/detection/output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug/ckpt/checkpoint_epoch_30.pth \
  --batch_size 1 \
  --eval_tag detzero_eval
```

### Expected Result

Should match DetZero's result: **~0.977 AP** for Vehicle on test/val split

### Output Location

Results will be saved to:
```
/home/aimob/projects/OpenPCDet/output/waymo_models/centerpoint_detzero/detzero_eval/eval/
```

## Troubleshooting

### If you get module import errors:
```bash
# Make sure you're in the OpenPCDet directory
cd /home/aimob/projects/OpenPCDet

# Verify installation
python -c "import pcdet; print('Success!')"

# If still fails, reinstall:
pip uninstall pcdet
pip install -e . --user
```

### If evaluation fails with shape mismatch:
- Double-check that the config matches DetZero exactly
- Verify voxel sizes: DetZero uses [0.1, 0.1, 0.15], not [0.32, 0.32, 6.0]

### If you get CUDA errors:
```bash
# Reduce batch size
python tools/test.py ... --batch_size 1
```

## Alternative: Use a Virtual Environment

If you prefer to keep OpenPCDet isolated:

```bash
cd /home/aimob/projects/OpenPCDet

# Create venv (if not exists)
python -m venv venv_openpcdet
source venv_openpcdet/bin/activate

# Install
pip install -e .
pip install -r requirements.txt

# Run evaluation (with venv activated)
python tools/test.py ... [same as above]
```

## Comparison with DetZero

### Advantages of OpenPCDet evaluation:
- Standard evaluation framework
- Easy comparison with other models
- Better visualization tools
- Community support

### Advantages of DetZero evaluation:
- Already working (0.977 AP verified)
- Includes refinement pipeline
- Optimized for your workflow

## Summary

✓ Config files created and matched to DetZero
⏳ OpenPCDet installation in progress
→ Once installed, run the command above to evaluate

Expected result: Same ~0.977 AP as DetZero baseline
