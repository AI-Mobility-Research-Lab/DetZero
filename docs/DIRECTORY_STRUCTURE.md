# DetZero Directory Structure

## Overview

```
DetZero/
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies
├── LICENSE                      # Project license
│
├── docs/                        # 📚 Documentation
│   ├── PROJECT_STATUS.md       # Current status (share this!)
│   ├── DIRECTORY_STRUCTURE.md  # This file
│   ├── README_8K_PIPELINE.md   # 8K dataset pipeline
│   ├── BACKGROUND_EXECUTION_GUIDE.md
│   │
│   ├── training/               # Training documentation
│   │   ├── TRAINING_GUIDE.md
│   │   ├── TRAINING_FIX_SUMMARY.md
│   │   ├── TRAINING_ACTUALLY_RUNNING.md
│   │   ├── TRAINING_STATUS_FINAL.md
│   │   ├── READY_TO_TRAIN.md
│   │   └── BACKGROUND_TRAINING_GUIDE.md
│   │
│   ├── conversion/             # Dataset conversion docs
│   │   ├── CONVERSION_IMPLEMENTATION_SUMMARY.md
│   │   ├── CONVERSION_SUCCESS.md
│   │   ├── QUICK_START_CONVERSION.md
│   │   └── DATA_GENERATED_SUCCESS.md
│   │
│   ├── analysis/               # Performance analysis
│   │   ├── performance_summary.md
│   │   ├── RESULTS_SUMMARY.md
│   │   ├── WEB_VISUALIZER_SUMMARY.md
│   │   └── VISUALIZATION_GUIDE.md
│   │
│   ├── deployment/             # Deployment guides
│   │   ├── DEPLOYMENT_STATUS.md
│   │   ├── DEPLOYMENT_SUCCESS.md
│   │   └── README_DEPLOYMENT.md
│   │
│   └── archive/                # Historical documents
│       ├── BUG_FIX_SUMMARY.md
│       ├── CURRENT_ISSUE_SUMMARY.md
│       ├── DETECTION_ISSUE_SUMMARY.md
│       ├── DETECTION_READY.md
│       ├── DETZERO_COMPATIBILITY_TEST_RESULTS.md
│       ├── FINAL_FIX_SUMMARY.md
│       ├── FIXED_IMPORT_ISSUE.md
│       ├── FIX_WEB_VISUALIZER.md
│       ├── GPU_MEMORY_FIX.md
│       ├── PROJECT_SUMMARY.md
│       ├── QUICK_FIX.txt
│       └── TRACKING_COMPATIBILITY_TEST_RESULTS.md
│
├── scripts/                     # 🛠️ Utility Scripts
│   ├── train_8k_waymo.sh       # Main training script
│   ├── check_training_status.sh # Status monitoring
│   ├── migrate_to_tmux.sh      # Persistence setup
│   ├── test_training_setup.py  # Pre-training validation
│   ├── test_8k_detection.py    # Detection testing
│   ├── test_augmentor_fix.py   # Augmentation testing
│   │
│   ├── conversion/             # Dataset conversion
│   │   ├── convert_nuscenes_to_detzero.py  # Main converter
│   │   ├── data_reader.py      # Dataset loading
│   │   ├── class_mapper.py     # Class mapping
│   │   ├── sequence_builder.py # Sequence creation
│   │   ├── format_converter.py # Format transformation
│   │   ├── file_writer.py      # Output writing
│   │   ├── validator.py        # Data validation
│   │   ├── logger_config.py    # Logging setup
│   │   └── tests/              # Unit tests
│   │
│   ├── generate_ablation_data.py    # Ablation study
│   ├── prepare_ablation_viz.py      # Visualization prep
│   └── 8k_pipeline/                 # 8K pipeline scripts
│
├── detection/                   # 🎯 Detection Module
│   ├── tools/                  # Training & testing tools
│   │   ├── train.py           # Training script
│   │   ├── test.py            # Testing script
│   │   ├── train_utils.py     # Training utilities
│   │   └── cfgs/              # Configuration files
│   │       ├── det_model_cfgs/
│   │       │   ├── centerpoint_1sweep_8k.yaml  # 8K model config
│   │       │   └── centerpoint_waymo_8k.yaml
│   │       └── det_dataset_cfgs/
│   │           └── waymo_8k.yaml               # 8K dataset config
│   │
│   ├── detzero_det/           # Detection implementation
│   │   ├── datasets/          # Dataset loaders
│   │   │   ├── dataset.py
│   │   │   ├── waymo/
│   │   │   │   ├── waymo_dataset.py
│   │   │   │   └── waymo_utils.py
│   │   │   └── augmentor/
│   │   │       ├── data_augmentor.py
│   │   │       └── augmentor_utils.py  # ✅ Fixed empty gt_boxes
│   │   ├── models/            # Model architectures
│   │   └── ops/               # Custom operations
│   │
│   └── output/                # 🎓 Training Outputs
│       └── cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k/
│           ├── ckpt/          # Model checkpoints
│           ├── tensorboard/   # TensorBoard logs
│           └── log_train_*.txt # Training logs
│
├── tracking/                   # 🎬 Tracking Module
│   ├── tools/                 # Tracking tools
│   └── detzero_track/         # Tracking implementation
│
├── refinement/                 # ✨ Refinement Module
│   ├── tools/                 # Refinement tools
│   └── detzero_refine/        # Refinement implementation
│       ├── grm/               # Global Refinement Module
│       ├── prm/               # Propagation Refinement Module
│       └── crm/               # Confidence Refinement Module
│
├── data/                       # 💾 Datasets
│   ├── waymo_8k/              # ✅ Converted 8K dataset
│   │   ├── waymo_processed_data/  # 72 sequence files
│   │   │   └── segment-scene_*/   # 100 frames each
│   │   ├── ImageSets/         # Train/val splits
│   │   │   ├── train.txt      # 7,200 frames
│   │   │   └── val.txt        # 800 frames
│   │   └── nuscenes_8k_detzero.yaml  # Dataset config
│   │
│   └── waymo/                 # Original 400-frame dataset
│
├── web_visualizer/             # 🎨 Visualization Tools
│   ├── index.html             # Main visualizer
│   ├── ablation.html          # Ablation study viewer
│   ├── ablation.js            # Visualization logic
│   └── debug.html             # Debug viewer
│
├── utils/                      # 🔧 Utility Functions
│   └── detzero_utils/         # DetZero utilities
│
└── .kiro/                      # 🤖 Kiro AI Configuration
    ├── specs/                 # Project specifications
    │   └── nuscenes-8k-to-detzero-conversion/
    │       ├── requirements.md
    │       ├── design.md
    │       └── tasks.md
    └── steering/              # AI steering files
```

## Key Directories

### 📚 docs/
All documentation organized by category. Start with `PROJECT_STATUS.md` for current status.

### 🛠️ scripts/
Utility scripts for training, testing, and data processing. Main entry points:
- `train_8k_waymo.sh` - Start training
- `check_training_status.sh` - Check training progress
- `conversion/convert_nuscenes_to_detzero.py` - Convert datasets

### 🎯 detection/
Detection module with training tools, model implementations, and outputs.

### 💾 data/
Datasets in DetZero format. The `waymo_8k/` directory contains the converted 8K dataset.

### 🎨 web_visualizer/
Interactive visualization tools for viewing detection results and ablation studies.

## Important Files

### For Sharing
- `docs/PROJECT_STATUS.md` - Comprehensive status report (share this!)
- `docs/DIRECTORY_STRUCTURE.md` - This file

### For Training
- `scripts/train_8k_waymo.sh` - Training script
- `detection/tools/cfgs/det_model_cfgs/centerpoint_1sweep_8k.yaml` - Model config
- `detection/tools/cfgs/det_dataset_cfgs/waymo_8k.yaml` - Dataset config

### For Monitoring
- `scripts/check_training_status.sh` - Quick status check
- `detection/output/.../log_train_*.txt` - Training logs
- `detection/output/.../ckpt/` - Model checkpoints

### For Understanding
- `README.md` - Main project documentation
- `docs/training/TRAINING_GUIDE.md` - Training guide
- `docs/conversion/CONVERSION_IMPLEMENTATION_SUMMARY.md` - Conversion details
- `docs/analysis/performance_summary.md` - Ablation study results

## File Organization Principles

1. **Documentation** (`docs/`) - All markdown files organized by category
2. **Scripts** (`scripts/`) - Executable scripts and utilities
3. **Source Code** (`detection/`, `tracking/`, `refinement/`) - Module implementations
4. **Data** (`data/`) - Datasets and processed data
5. **Outputs** (`detection/output/`) - Training outputs, logs, checkpoints
6. **Visualization** (`web_visualizer/`) - Interactive visualization tools

## Quick Navigation

```bash
# View project status
cat docs/PROJECT_STATUS.md

# Check training
./scripts/check_training_status.sh

# View training logs
tail -f detection/output/cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt

# View ablation study
open web_visualizer/ablation.html

# Check dataset
ls data/waymo_8k/waymo_processed_data/
```

## Cleanup Summary

Moved 30+ scattered markdown files from root directory into organized structure:
- ✅ Training docs → `docs/training/`
- ✅ Conversion docs → `docs/conversion/`
- ✅ Analysis docs → `docs/analysis/`
- ✅ Deployment docs → `docs/deployment/`
- ✅ Historical docs → `docs/archive/`

Root directory now contains only:
- `README.md` - Main documentation
- `requirements.txt` - Dependencies
- `LICENSE` - License file
