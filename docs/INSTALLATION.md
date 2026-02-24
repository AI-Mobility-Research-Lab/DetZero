# DetZero Installation Guide

## Quick Start (Recommended)

For GCP V100 deployment with the **working configuration** (PyTorch 1.10 + CUDA 11.1):

```bash
# From local machine - create V100 instance
export GCP_PROJECT_ID="your-project-id"
bash cloud/gcp_setup_v100_standard.sh

# SSH into instance
gcloud compute ssh detzero-v100-training --zone=us-central1-a --project=your-project-id

# Run setup script (PyTorch 1.10 + CUDA 11.1)
wget https://raw.githubusercontent.com/AI-Mobility-Research-Lab/DetZero/main/cloud/gcp_instance_setup_pytorch110.sh
bash gcp_instance_setup_pytorch110.sh

# Upload dataset
# (from local machine)
gcloud compute scp --recurse /path/to/waymo_8k detzero-v100-training:~/ --zone=us-central1-a --project=your-project-id

# Start training
tmux new -s training
cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh
```

## System Requirements

### Working Configuration (Verified)
- Ubuntu 22.04 LTS
- NVIDIA GPU with Compute Capability 7.0+ (V100, A100, etc.)
- NVIDIA Driver 535+ (tested with 580.126.09)
- **CUDA Toolkit 11.1** (critical - not 11.7, not 12.x)
- **Python 3.8-3.10**
- **PyTorch 1.10** (critical - not 1.13, not 2.x)
- 16GB+ GPU VRAM recommended for training

### Why These Specific Versions?

DetZero's CUDA extensions were built for PyTorch 1.10 + CUDA 11.1. Using newer versions requires extensive code refactoring:
- **PyTorch 2.x**: Removed THC headers, deprecated APIs
- **CUDA 12.x**: Version mismatch with PyTorch 1.10
- **PyTorch 1.13+**: Different CUDA version requirements

See [Lessons Learned](LESSONS_LEARNED.md) for detailed version compatibility analysis.

## Manual Installation

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    git wget curl vim tmux htop \
    build-essential python3-pip python3-dev \
    ubuntu-drivers-common
```

### 2. Install NVIDIA Drivers

```bash
# Install drivers
sudo ubuntu-drivers install

# Reboot to load drivers
sudo reboot

# Verify after reboot
nvidia-smi
```

### 3. Install CUDA Toolkit 12.1

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-1

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvcc --version
```

### 4. Install Python Dependencies

```bash
# Install PyTorch 2.1 with CUDA 12.1
pip3 install -r requirements-cuda121.txt

# Verify PyTorch
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### 5. Clone Repository

```bash
cd ~
git clone https://github.com/AI-Mobility-Research-Lab/DetZero.git
cd DetZero
```

### 6. Build CUDA Extensions

```bash
# Add modules to Python path
export PYTHONPATH="${PYTHONPATH}:${HOME}/DetZero/detection:${HOME}/DetZero/utils"
echo 'export PYTHONPATH="${PYTHONPATH}:${HOME}/DetZero/detection:${HOME}/DetZero/utils"' >> ~/.bashrc

# Build detection extensions
cd ~/DetZero/detection
python3 setup.py develop --user

# Build utils extensions
cd ~/DetZero/utils
python3 setup.py develop --user

# Verify extensions
python3 -c "from detzero_utils.ops.roiaware_pool3d import roiaware_pool3d_cuda; print('CUDA extensions loaded!')"
```

### 7. Prepare Dataset

```bash
# Create data directory
mkdir -p ~/DetZero/data/waymo_8k

# Upload your dataset (from local machine)
gcloud compute scp --recurse \
  /path/to/your/waymo_8k \
  your-instance:~/DetZero/data/ \
  --zone=your-zone \
  --project=your-project
```

## Training

```bash
# Start training in tmux (recommended)
tmux new -s training
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh

# Detach from tmux: Ctrl+B, then D
# Reattach: tmux attach -t training
```

## Troubleshooting

### CUDA Extension Build Fails

If you see `THC/THC.h: No such file or directory`:
- Ensure you're using PyTorch 2.1.2 (not 2.5+)
- The THC headers were removed in PyTorch 2.x
- Our code has been patched to remove THC dependencies

### PyTorch Version Mismatch

If you see CUDA version mismatch errors:
- Ensure CUDA Toolkit version matches PyTorch CUDA version
- Use PyTorch 2.1.2 with CUDA 12.1
- Check: `nvcc --version` and `python3 -c "import torch; print(torch.version.cuda)"`

### NumPy Version Issues

If you see NumPy 2.x compatibility warnings:
```bash
pip3 install "numpy<2.0"
```

### Module Not Found Errors

If you see `ModuleNotFoundError: No module named 'detzero_utils'`:
```bash
export PYTHONPATH="${PYTHONPATH}:${HOME}/DetZero/detection:${HOME}/DetZero/utils"
```

## Verified Configurations

### GCP V100 (Tested)
- Instance: n1-highmem-8 + 1x V100 16GB
- OS: Ubuntu 22.04 LTS
- Driver: 580.126.09
- CUDA: 12.1
- PyTorch: 2.1.2+cu121
- Cost: ~$2.48/hour

### Local RTX 4060 (Not Recommended)
- 8GB VRAM insufficient for batch_size=1
- Frequent OOM crashes
- Use cloud GPU instead

## Performance

- V100 16GB: ~4-5 hours for 30 epochs (batch_size=4)
- A100 40GB: ~2-3 hours for 30 epochs (batch_size=8)
- RTX 4060 8GB: Not viable (OOM issues)

## Next Steps

After installation, see:
- [Training Guide](TRAINING.md) - Training configuration and monitoring
- [Dataset Guide](DATASET.md) - Dataset preparation and format
- [GCP Guide](../cloud/GCP_DEPLOYMENT_GUIDE.md) - Cloud deployment details
