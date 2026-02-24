# Experimental Configuration Files

These configuration files were created during development and testing but are not part of the main training pipeline.

## Detection Configs (Unused)

### Dataset Configs
- `detection/tools/cfgs/det_dataset_cfgs/nuscenes_custom_8k.yaml` - Early nuScenes config (before conversion to Waymo format)
- `detection/tools/cfgs/det_dataset_cfgs/waymo_custom_1sweep.yaml` - Old custom Waymo config
- `detection/tools/cfgs/det_dataset_cfgs/waymo_custom_1sweep_noaug.yaml` - Old custom Waymo config without augmentation

### Model Configs
- `detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml` - Early nuScenes model config
- `detection/tools/cfgs/det_model_cfgs/centerpoint_waymo_8k.yaml` - Alternative 8K config
- `detection/tools/cfgs/det_model_cfgs/centerpoint_1sweep_custom.yaml` - Old custom model config

## Tracking Configs (Unused)

### Dataset Configs
- `tracking/tools/cfgs/tk_dataset_cfgs/nuscenes_custom_8k_dataset.yaml` - Early nuScenes tracking config
- `tracking/tools/cfgs/tk_dataset_cfgs/waymo_custom_dataset.yaml` - Old custom Waymo tracking config

### Model Configs
- `tracking/tools/cfgs/tk_model_cfgs/detzero_track_8k.yaml` - Early nuScenes tracking model
- `tracking/tools/cfgs/tk_model_cfgs/waymo_detzero_track_custom.yaml` - Old custom tracking model

## Active Configs (Currently Used)

### Detection
- `detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml` - Active 8K dataset config
- `detection/tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml` - Active model config

### Training Script
- `scripts/train_8k_waymo.sh` - Main training script

## Recommendation

These experimental configs can be:
1. Kept for reference (current state)
2. Moved to `configs/experimental/` directory
3. Deleted if no longer needed

They are currently untracked by git and won't be committed unless explicitly added.
