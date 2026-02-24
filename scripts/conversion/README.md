# nuScenes 8K to DetZero Waymo Format Conversion

This package converts the OpenPCDet 8K nuScenes dataset (7,200 training + 800 validation samples) to DetZero's Waymo format for use in detection, tracking, and refinement.

## Quick Start

### Basic Usage

```bash
# From DetZero root directory
./scripts/run_conversion.sh
```

This uses default paths:
- Source: `/home/aimob/projects/OpenPCDet/data/nuscenes_custom`
- Output: `./data/waymo_8k`
- Version: `v1.0-tak_8k_human_combined`

### Custom Paths

```bash
./scripts/run_conversion.sh \
    --source /path/to/nuscenes \
    --output /path/to/output \
    --version v1.0-tak_8k_human_combined \
    --workers 8
```

### Validation Only

```bash
./scripts/run_conversion.sh --validate-only --output ./data/waymo_8k
```

## Direct Python Usage

```bash
cd scripts/conversion

python3 convert_nuscenes_to_detzero.py \
    --source_path /home/aimob/projects/OpenPCDet/data/nuscenes_custom \
    --output_path ../../data/waymo_8k \
    --version v1.0-tak_8k_human_combined \
    --splits train val \
    --workers 8
```

## Arguments

- `--source_path`: Path to OpenPCDet nuScenes data directory (required)
- `--output_path`: Output directory for converted data (required)
- `--version`: Dataset version (default: v1.0-tak_8k_human_combined)
- `--splits`: Dataset splits to convert (default: train val)
- `--workers`: Number of parallel workers (default: CPU count - 1)
- `--validate-only`: Only run validation without conversion

## Output Structure

```
data/waymo_8k/
├── waymo_processed_data/
│   ├── segment-{scene_token_1}_with_camera_labels/
│   │   ├── segment-{scene_token_1}_with_camera_labels.pkl
│   │   ├── 0000.npy
│   │   ├── 0001.npy
│   │   └── ...
│   ├── segment-{scene_token_2}_with_camera_labels/
│   │   └── ...
│   └── ...
├── ImageSets/
│   ├── train.txt
│   └── val.txt
└── nuscenes_8k_detzero.yaml
```

## Components

### Data Reader (`data_reader.py`)
Loads nuScenes info files and point cloud data from OpenPCDet format.

### Class Mapper (`class_mapper.py`)
Maps nuScenes object classes to Waymo taxonomy:
- car, truck, bus, trailer, construction_vehicle → Vehicle
- pedestrian → Pedestrian
- bicycle, motorcycle → Cyclist

### Sequence Builder (`sequence_builder.py`)
Groups frames by scene token and maintains temporal ordering.

### Format Converter (`format_converter.py`)
Transforms nuScenes annotations and metadata to DetZero Waymo structure.

### File Writer (`file_writer.py`)
Writes converted data to disk in DetZero format.

### Validator (`validator.py`)
Verifies conversion integrity and computes statistics.

## Performance

Expected conversion time for 8,000 frames:
- 8 CPU cores: ~30-60 minutes
- 16 CPU cores: ~15-30 minutes

Processing rate: ~100-200 frames/second (depends on I/O speed)

## Troubleshooting

### Missing Info Files

Error: `Info file not found: .../nuscenes_infos_1sweeps_train.pkl`

Solution: Verify the source path and version are correct. The info files should be at:
```
{source_path}/{version}/nuscenes_infos_1sweeps_{split}.pkl
```

### Point Cloud Load Failures

Error: `Point cloud file not found: ...`

Solution: Check that point cloud .bin files exist in the source dataset. The conversion expects nuScenes point clouds in .bin format.

### Memory Issues

If conversion fails with memory errors, reduce the number of workers:
```bash
./scripts/run_conversion.sh --workers 2
```

### Validation Failures

Run validation to check converted data:
```bash
./scripts/run_conversion.sh --validate-only --output ./data/waymo_8k
```

## Integration with DetZero

After conversion, update your detection config to use the new dataset:

```yaml
# detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml
DATASET: 'WaymoDetectionDataset'
DATA_PATH: '../../data/waymo_8k'
PROCESSED_DATA_TAG: 'waymo_processed_data'
```

Then run detection:
```bash
cd detection
python tools/test.py \
    --cfg_file tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt ../detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --data_path ../data/waymo_8k
```

## Expected Improvements

Compared to the original 400-frame dataset:

- **Detection**: 15-25 boxes/frame (vs 9.5)
- **Tracking**: Continuous sequences, fewer ID switches
- **Refinement**: +10-30% boxes (vs +321%), CRM scores 0.7-0.9 (vs 0.366)

## Logs

Conversion logs are saved to `logs/conversion_{timestamp}.log` with detailed progress and error information.
