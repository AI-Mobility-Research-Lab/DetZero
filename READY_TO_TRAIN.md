# 🚀 Ready to Train DetZero!

All issues have been identified and fixed. Here's what to do:

## Quick Start (Recommended)

SSH into your GCP instance and run:

```bash
cd ~/DetZero
bash START_TRAINING.sh
```

This single command will:
1. ✓ Fix the conda environment (Python 3.9)
2. ✓ Generate pickle files with correct paths
3. ✓ Verify dataset integrity
4. ✓ Start training in tmux (persistent)

Training will run for ~4-5 hours and survive SSH disconnections.

## What Was Fixed

### 1. Environment Configuration
- **Fixed**: `environment.yml` now uses Python 3.9 (was 3.10)
- **Added**: NumPy <2.0 constraint for PyTorch 1.10 compatibility

### 2. Pickle File Generation
- **Issue**: Empty pickle files with 0 samples
- **Cause**: Script tried to process from missing TFRecord files
- **Fix**: New script generates from existing processed data at `~/waymo_8k/waymo_processed_data/`

### 3. File Path Corrections
- **Issue**: Paths referenced `/home/aimob/projects/DetZero/` (doesn't exist)
- **Actual**: `/home/aimob/DetZero/`
- **Fix**: Pickle files now generated with correct paths

### 4. Training Persistence
- **Issue**: Training stops when SSH disconnects
- **Fix**: Training runs in tmux session (survives disconnections)

## Manual Steps (If You Prefer)

### Step 1: Fix Setup
```bash
cd ~/DetZero
bash fix_training_setup.sh
```

This will:
- Verify conda environment
- Check dataset structure
- Create necessary symlinks
- Generate pickle files
- Verify generated files have data

### Step 2: Start Training
```bash
# Option A: Direct (see output immediately, but stops on SSH disconnect)
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh

# Option B: With tmux (persistent, recommended)
tmux new -s training
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh
# Detach: Ctrl+B, then D
```

## Verify Before Training

Check that everything is ready:

```bash
# 1. Conda environment
conda activate detzero
which python  # Should show: /home/aimob/miniconda3/envs/detzero/bin/python
python --version  # Should show: Python 3.9.x

# 2. Dataset
ls -lh ~/waymo_8k/waymo_processed_data/ | head
# Should show: segment-* directories

# 3. Pickle files
python3 -c "import pickle; data=pickle.load(open('/home/aimob/DetZero/data/waymo_8k/waymo_infos_train.pkl','rb')); print(f'Train: {len(data)} samples')"
# Should show: Train: 7200 samples (or similar)

# 4. GPU
nvidia-smi
# Should show: Tesla V100-SXM2-16GB
```

## During Training

### Monitor Progress
```bash
# Attach to tmux session
tmux attach -t training

# Detach (keep training running)
# Press: Ctrl+B, then D
```

### Check GPU Usage
```bash
watch -n 1 nvidia-smi
```

### View Output Directory
```bash
ls -lh ~/DetZero/detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/
```

## After Training

### Stop Instance (Important!)
```bash
# From your local machine
gcloud compute instances stop detzero-v100-training \
    --zone=us-central1-a \
    --project=detzeroaimob
```

V100 costs ~$2.48/hour. Stopping saves money!

### Download Checkpoints (Optional)
```bash
# From your local machine
gcloud compute scp --recurse \
    detzero-v100-training:~/DetZero/detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/ \
    ./local_output/ \
    --zone=us-central1-a \
    --project=detzeroaimob
```

## Training Configuration

- **Model**: CenterPoint (1-sweep)
- **Dataset**: Waymo 8K (7,200 train, 800 val)
- **Batch Size**: 4 (optimized for V100 16GB)
- **Epochs**: 30
- **Workers**: 6
- **Expected Time**: ~4-5 hours
- **GPU**: Tesla V100-SXM2-16GB
- **CUDA**: 11.1
- **PyTorch**: 1.10.0

## Troubleshooting

See `ANSWERS_TO_QUESTIONS.md` for detailed explanations of:
- Why pickle files were empty
- Why training crashed with FileNotFoundError
- Why pip was using system Python
- How tmux provides persistence
- GCP billing and cost management

## Files Created

- `fix_training_setup.sh` - Fixes all setup issues
- `START_TRAINING.sh` - One-command setup and start
- `TRAINING_GUIDE.md` - Comprehensive reference guide
- `ANSWERS_TO_QUESTIONS.md` - Detailed Q&A
- `regenerate_pickle_files.py` - Python script for pickle generation

## Ready? Let's Go! 🎯

```bash
cd ~/DetZero
bash START_TRAINING.sh
```

The script will guide you through the process. Training will start automatically in tmux.

Good luck with your training! 🚀
