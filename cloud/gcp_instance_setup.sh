#!/bin/bash
# Instance setup script - Run this on the GCP A100 instance

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
    git \
    wget \
    curl \
    vim \
    tmux \
    htop \
    build-essential \
    python3-pip \
    python3-dev

# Verify NVIDIA driver
echo "Verifying NVIDIA driver..."
nvidia-smi

# Install CUDA toolkit (if not already installed)
if ! command -v nvcc &> /dev/null; then
    echo "Installing CUDA toolkit..."
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt-get update
    sudo apt-get -y install cuda-toolkit-12-1
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    source ~/.bashrc
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
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
echo "Creating data directory..."
sudo mkdir -p /mnt/data
sudo chown $USER:$USER /mnt/data
ln -sf /mnt/data ~/DetZero/data/waymo_8k

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "GPU Info:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
echo ""
echo "Next steps:"
echo "1. Upload dataset: gsutil -m rsync -r gs://your-bucket/waymo_8k /mnt/data/"
echo "2. Or use gcloud compute scp to copy from local machine"
echo "3. Start training: cd ~/DetZero && bash scripts/train_8k_waymo_a100.sh"
echo "=========================================="
