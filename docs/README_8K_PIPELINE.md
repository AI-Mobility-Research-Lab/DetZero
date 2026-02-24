# DetZero 8K Pipeline - Organized Structure

## Directory Structure

```
DetZero/
├── scripts/
│   ├── 8k_pipeline/
│   │   ├── run_detection_8k.py              # Main detection script
│   │   ├── run_8k_pipeline.sh               # Full pipeline automation
│   │   ├── run_detection_8k_background.sh   # Run with nohup
│   │   ├── run_detection_8k_tmux.sh         # Run with tmux
│   │   ├── run_detection_8k_screen.sh       # Run with screen
│   │   └── test_8k_setup.py                 # Verify setup
│   ├── generate_ablation_data.py            # Generate ablation data
│   └── prepare_ablation_viz.py              # Prepare visualization
│
├── docs/
│   ├── 8k_pipeline/
│   │   ├── DATASET_ANALYSIS_AND_RECOMMENDATION.md
│   │   ├── 8K_PIPELINE_GUIDE.md
│   │   ├── RETRAINING_SUMMARY.md
│   │   └── QUICK_START_8K.txt
│   └── ablation_study/
│       └── ABLATION_STUDY_GUIDE.md
│
├── logs/                                     # All log files go here
├── output_8k/                                # Pipeline outputs
│   ├── detection/
│   ├── tracking/
│   └── refining/
│
├── detection/                                # Detection module
├── tracking/                                 # Tracking module
├── refining/                                 # Refinement module
└── web_visualizer/                           # Web visualization
```

## Quick Start

### 1. Verify Setup
```bash
python3 scripts/8k_pipeline/test_8k_setup.py
```

### 2. Run Detection (Choose One)

**Option A: Foreground (see output)**
```bash
python3 scripts/8k_pipeline/run_detection_8k.py
```

**Option B: Background with nohup (recommended)**
```bash
./scripts/8k_pipeline/run_detection_8k_background.sh
# Monitor: tail -f logs/detection_8k.log
```

**Option C: Tmux session**
```bash
./scripts/8k_pipeline/run_detection_8k_tmux.sh
# Attach: tmux attach -t detzero_detection_8k
```

**Option D: Screen session**
```bash
./scripts/8k_pipeline/run_detection_8k_screen.sh
# Attach: screen -r detzero_detection_8k
```

### 3. Run Full Pipeline
```bash
./scripts/8k_pipeline/run_8k_pipeline.sh
```

## Documentation

- **Quick Reference**: `docs/8k_pipeline/QUICK_START_8K.txt`
- **Complete Guide**: `docs/8k_pipeline/8K_PIPELINE_GUIDE.md`
- **Setup Summary**: `docs/8k_pipeline/RETRAINING_SUMMARY.md`
- **Analysis**: `docs/8k_pipeline/DATASET_ANALYSIS_AND_RECOMMENDATION.md`

## Monitoring

All logs are in the `logs/` directory:
```bash
# Detection logs
tail -f logs/detection_8k.log

# Pipeline logs
tail -f logs/pipeline_8k.log

# Nohup output
tail -f nohup_detection_8k.out
```

## Expected Results

- **Detection**: 800 frames, 15-25 boxes/frame, 0.85-0.95 avg score
- **Tracking**: Continuous tracks, better ID consistency
- **Refinement**: +10-30% boxes (vs current +321%), 0.7-0.9 scores (vs current 0.366)

## Next Steps

1. Run detection test (30 min)
2. Validate results
3. Run full pipeline (10-16 hours)
4. Compare with old results
5. Deploy if better

For detailed instructions, see `docs/8k_pipeline/8K_PIPELINE_GUIDE.md`
