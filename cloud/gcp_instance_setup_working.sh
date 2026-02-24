#!/bin/bash
# Working instance setup script for Ubuntu 22.04 on GCP

set -e

echo "=========================================="
echo "DetZero Instance Setup"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt-get install -y \
    git wget curl vim tmux htop \
    build-essential python3-pip python3-dev

# Install NVIDIA drivers (GCP provides these in their repos)
echo "Installing NVIDIA drivers..."
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers install

# Wait for driver to load
echo "Waiting for NVIDIA driver to initialize..."
sleep 10

# Verify NVIDIA driver
echo "Verifying NVIDIA driver..."
nvidia-smi || {
    echo "Driver not loaded yet, trying manual load..."
    sudo modprobe nvidia
    sleep 5
    nvidia-smi
}

# Install CUDA toolkit
echo "Installing CUDA toolkit..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-1

# Set up environment
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install PyTorch (CUDA 12.1)
echo "Installing PyTorch..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other Python dependencies
echo "Installing Python dependencies..."
pip3 install numpy scipy pyyaml easydict tqdm tensorboard

# Install spconv
echo "Installing spconv..."
pip3 install spconv-cu121

# Clone DetZero repository
echo "Cloning DetZero repository..."
cd ~
if [ ! -d "DetZero" ]; then
    git clone https://github.com/AI-Mobility-Research-Lab/DetZero.git
    cd DetZero
else
    cd DetZero
    git pull
fi

# Build CUDA extensions
echo "Building CUDA extensions..."
cd detection/detzero_det/ops
python3 setup.py develop
cd ../../..

cd utils/detzero_utils/ops/iou3d_nms
python3 setup.py develop
cd ../../../..

# Create data directory
mkdir -p ~/waymo_8k
ln -sf ~/waymo_8k ~/DetZero/data/waymo_8k

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "GPU Info:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
echo ""
echo "CUDA Version:"
nvcc --version
echo ""
echo "PyTorch CUDA:"
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
echo ""
echo "Disk Space:"
df -h ~
echo ""
echo "Next steps:"
echo "1. Upload dataset from local machine:"
echo "   gcloud compute scp --recurse /home/aimob/projects/OpenPCDet/data/waymo_8k detzero-v100-training:~/ --zone=us-central1-a --project=detzeroaimob"
echo ""
echo "2. Start training (use tmux):"
echo "   tmux new -s training"
echo "   cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh"
echo "   # Detach: Ctrl+B then D"
echo "=========================================="
