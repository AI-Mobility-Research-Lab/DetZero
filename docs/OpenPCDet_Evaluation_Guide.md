# Evaluating DetZero CenterPoint in OpenPCDet

## Overview

DetZero is built on top of OpenPCDet, so the CenterPoint model trained in DetZero can be evaluated in OpenPCDet with minimal conversion. The checkpoint format is already compatible - both use the same PyTorch structure.

## Quick Answer: Yes, It's Compatible!

The checkpoint format is already OpenPCDet-compatible:
- ✓ Same architecture (CenterPoint)
- ✓ Same checkpoint structure (`model_state`, `epoch`, `optimizer_state`)
- ✓ Same module naming (e.g., `backbone3d`, `backbone2d`, `dense_head`)

## Method 1: Direct Evaluation in OpenPCDet (Recommended if you have OpenPCDet installed)

### Step 1: Install OpenPCDet

```bash
# Clone OpenPCDet
git clone https://github.com/open-mmlab/OpenPCDet.git
cd OpenPCDet

# Install dependencies
pip install -r requirements.txt
python setup.py develop
```

### Step 2: Prepare Your Data in OpenPCDet Format

Your `waymo_custom` data needs to be in OpenPCDet's expected structure:

```bash
OpenPCDet/data/waymo/
├── waymo_infos_train.pkl
├── waymo_infos_val.pkl
├── waymo_infos_test.pkl
└── waymo_custom_processed_data/
    └── segment-*/
        └── *.npy
```

You can symlink your DetZero data:

```bash
cd OpenPCDet/data
ln -s /home/aimob/projects/DetZero/data/waymo_custom waymo_custom
```

### Step 3: Create OpenPCDet Config

Copy your DetZero config and adapt it to OpenPCDet format:

```bash
# In OpenPCDet directory
cp tools/cfgs/waymo_models/centerpoint.yaml \
   tools/cfgs/waymo_models/centerpoint_custom.yaml
```

Edit `centerpoint_custom.yaml` to match your DetZero config settings (voxel size, point cloud range, etc.).

### Step 4: Run Evaluation

```bash
cd OpenPCDet/tools

python test.py \
  --cfg_file cfgs/waymo_models/centerpoint_custom.yaml \
  --ckpt /home/aimob/projects/DetZero/detection/output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug/ckpt/checkpoint_epoch_30.pth \
  --eval_tag centerpoint_custom
```

## Method 2: Stay with DetZero (Simpler)

Since DetZero is based on OpenPCDet and you already have working evaluation (0.977 AP), you might not need OpenPCDet at all.

**Advantages of staying with DetZero:**
- Already set up and working
- Includes refinement pipeline (tracking + GRM/PRM/CRM)
- Optimized for your workflow

**When you need OpenPCDet:**
- You want to use OpenPCDet's visualization tools
- You want to compare with other OpenPCDet models
- You need OpenPCDet's data augmentation features
- You want to participate in Waymo challenges using OpenPCDet submission format

## Checkpoint Compatibility Check

DetZero checkpoint structure:
```python
{
    'epoch': 30,
    'it': iteration_number,
    'model_state': {
        'global_step': tensor([...]),
        'backbone3d.conv_input.0.weight': tensor([...]),
        'backbone3d.conv_input.1.weight': tensor([...]),
        'backbone2d.blocks.0.0.weight': tensor([...]),
        'dense_head.conv_cls.weight': tensor([...]),
        ...
    },
    'optimizer_state': {...},
    'version': 'detzero_det+0.1.0+051fad7'
}
```

This is **identical** to OpenPCDet's checkpoint format! No conversion needed.

## Data Format Compatibility

Your data format is already compatible:

**DetZero (current):**
```
data/waymo_custom/
├── waymo_infos_train.pkl
├── waymo_infos_val.pkl
├── waymo_infos_test.pkl
└── waymo_custom_processed_data/
```

**OpenPCDet expects:**
```
data/waymo/
├── waymo_infos_train.pkl
├── waymo_infos_val.pkl
├── waymo_infos_test.pkl
└── waymo_processed_data/  # or custom name
```

Just symlink or copy your data to OpenPCDet's `data/waymo/` directory.

## Potential Issues and Solutions

### Issue 1: Config File Differences

**Problem:** DetZero configs might have different keys than OpenPCDet.

**Solution:**
1. Compare your DetZero config with OpenPCDet's CenterPoint config
2. Adjust parameter names if needed
3. Key parameters to check:
   - `POINT_CLOUD_RANGE`
   - `VOXEL_SIZE`
   - `DATA_PROCESSOR`
   - `DATA_AUGMENTOR`

### Issue 2: Class Names

**Problem:** Custom class names might differ.

**Solution:**
```yaml
# In your OpenPCDet config
CLASS_NAMES: ['Vehicle', 'Pedestrian', 'Cyclist']  # Match your DetZero setup
```

### Issue 3: Dataset Class

**Problem:** DetZero uses custom dataset class.

**Solution:** OpenPCDet's `WaymoDataset` should work, but verify:
- Point feature dimensions match
- Coordinate frames are consistent
- Preprocessing steps are identical

## Verification Steps

After setting up OpenPCDet evaluation:

1. **Check model loads correctly:**
```python
import torch
ckpt = torch.load('checkpoint_epoch_30.pth', weights_only=False)
print("Model parameters:", len(ckpt['model_state']))
```

2. **Run inference on 1 sample:**
```bash
python test.py --cfg_file ... --ckpt ... --batch_size 1 --start_epoch 30 --eval_all
```

3. **Compare results with DetZero:**
   - DetZero result: 0.977 AP on test
   - OpenPCDet should produce same/similar result

## Recommended Workflow

### If you just want to evaluate:
```bash
# Stay with DetZero - it's already working!
cd /home/aimob/projects/DetZero/detection/tools
python test.py --cfg_file cfgs/det_model_cfgs/centerpoint_1sweep_custom.yaml \
  --ckpt ../output/.../checkpoint_epoch_30.pth
```

### If you need OpenPCDet features:
1. Install OpenPCDet
2. Symlink your data to OpenPCDet structure
3. Create matching config file
4. Run OpenPCDet evaluation with your checkpoint

### If you want both:
Keep DetZero for refinement pipeline, use OpenPCDet for baseline comparison and visualization.

## Summary

**Yes, your CenterPoint can be evaluated in OpenPCDet!**

- ✓ Checkpoint format is compatible (no conversion needed)
- ✓ Model architecture is the same
- ✓ Data format is compatible (may need symlinking)
- ⚠ Config file needs minor adaptation
- ⚠ Dataset class might need tweaking

**Recommendation:** If you're happy with DetZero's evaluation (0.977 AP), there's no strong reason to switch to OpenPCDet unless you need specific OpenPCDet features.
