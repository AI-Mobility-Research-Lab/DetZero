# Answers to Your Questions

## Q1: Why are the pickle files empty?

The pickle files at `~/waymo_8k/waymo_infos_*.pkl` are empty because the data preprocessing script failed or wasn't run correctly. The script expects:
- Raw TFRecord files in `~/waymo_8k/raw_data/` (which you don't have)
- OR already processed `.npy` files in `~/waymo_8k/waymo_processed_data/` (which you DO have)

The issue is that the script tried to process from TFRecords, found they were missing, and created empty pickle files.

**Solution**: Run `bash fix_training_setup.sh` which will generate pickle files from your existing processed data.

## Q2: Why does training crash with FileNotFoundError?

The error shows:
```
FileNotFoundError: [Errno 2] No such file or directory: 
'/home/aimob/projects/DetZero/data/waymo_8k/waymo_processed_data/segment-scene_0069_with_camera_labels/0071.npy'
```

The path has `/home/aimob/projects/DetZero/` but your actual path is `/home/aimob/DetZero/` (no "projects" folder).

This happened because:
1. The pickle files were generated with incorrect paths
2. OR the pickle files are referencing an old dataset location

**Solution**: Regenerate pickle files with correct paths using `fix_training_setup.sh`.

## Q3: Why is pip using system Python 3.10 instead of conda env?

You saw:
```bash
which pip
/home/aimob/.local/bin/pip
pip --version
pip 26.0.1 from /home/aimob/.local/lib/python3.10/site-packages/pip (python 3.10)
```

This means:
- The conda environment is NOT activated, OR
- The system pip is in your PATH before the conda pip

**Solution**:
```bash
# Properly activate conda
eval "$(conda shell.bash hook)"
conda activate detzero

# Verify
which python  # Should show: /home/aimob/miniconda3/envs/detzero/bin/python
which pip     # Should show: /home/aimob/miniconda3/envs/detzero/bin/pip
python --version  # Should show: Python 3.9.x
```

## Q4: Should we push and pull (Git)?

**Not necessary for training**, but recommended for backup:

```bash
# Add the fixed files
git add environment.yml fix_training_setup.sh TRAINING_GUIDE.md

# Commit
git commit -m "Fix training setup: Python 3.9, pickle generation script"

# Push (if you want to backup)
git push origin main
```

However, **DO NOT** commit:
- Pickle files (*.pkl) - they're large and machine-specific
- Model checkpoints - they're huge
- Dataset files - they're massive

These should be in `.gitignore`.

## Q5: Will training persist if SSH disconnects?

**NO** - if you run the script directly and SSH disconnects, training will stop.

**YES** - if you run in tmux, training continues even after SSH disconnects.

### Without tmux (NOT persistent):
```bash
bash scripts/train_8k_waymo_v100.sh
# If SSH disconnects → training stops ❌
```

### With tmux (PERSISTENT):
```bash
tmux new -s training
bash scripts/train_8k_waymo_v100.sh
# Press Ctrl+B, then D to detach
# If SSH disconnects → training continues ✓
```

You can disconnect, close your laptop, and training keeps running!

## Q6: Will GCP keep charging if I leave the instance running?

**YES** - GCP charges per hour while the instance is running, whether you're using it or not.

- **Running**: ~$2.48/hour (V100 GPU cost)
- **Stopped**: ~$0.10/hour (just disk storage)

**Best practice**:
1. Start training in tmux
2. Detach from tmux (Ctrl+B, D)
3. Exit SSH
4. Let it train (4-5 hours)
5. SSH back in to check progress
6. When done, STOP the instance:
   ```bash
   gcloud compute instances stop detzero-v100-training \
       --zone=us-central1-a --project=detzeroaimob
   ```

**Cost comparison**:
- Training for 5 hours: ~$12.40
- Leaving running for 24 hours: ~$59.52
- Stopped for 24 hours: ~$2.40

Always stop when not training!

## Q7: Why is conda still freezing?

If `conda install` or `conda update` is stuck at "still freezing", it means conda is solving dependencies. This can take a long time (10-30 minutes) for complex environments.

**Solutions**:
1. **Wait it out** - it will eventually finish
2. **Use mamba** (faster conda):
   ```bash
   conda install -n base conda-forge::mamba
   mamba install <package>  # Much faster
   ```
3. **Use pip** for Python packages (when possible):
   ```bash
   pip install <package>
   ```

For this project, the environment is already set up, so you shouldn't need to install more packages.

## Q8: Was the revised environment.yml pushed?

Looking at the file, it still has `python=3.10` which is wrong. I've fixed it to `python=3.9` in this session.

**To push the fix**:
```bash
cd ~/DetZero
git add environment.yml
git commit -m "Fix Python version to 3.9 for PyTorch 1.10 compatibility"
git push
```

But this is optional - the local fix is what matters for training.

## Summary of Actions Needed

1. **Fix the setup** (most important):
   ```bash
   cd ~/DetZero
   bash fix_training_setup.sh
   ```

2. **Start training in tmux**:
   ```bash
   tmux new -s training
   cd ~/DetZero
   bash scripts/train_8k_waymo_v100.sh
   # Detach: Ctrl+B, D
   ```

3. **Monitor progress** (optional):
   ```bash
   tmux attach -t training
   ```

4. **Stop instance when done**:
   ```bash
   gcloud compute instances stop detzero-v100-training \
       --zone=us-central1-a --project=detzeroaimob
   ```

That's it! The training should run for ~4-5 hours and save checkpoints to the output directory.
