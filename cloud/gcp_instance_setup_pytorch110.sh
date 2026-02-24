#!/bin/bash
# DetZero V100 Setup with PyTorch 1.10 + CUDA 11.1 (WORKING CONFIGURATION)
# This matches the original environment from docs/INSTALL.md

set -e

echo "=========================================="
echo "DetZero V100 Setup (PyTorch 1.10)"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt-get install -y \
    git wget curl vim tmux htop \
    build-essential python3-pip python3-dev \
    cmake

# Check if nvidia-smi works
if ! nvidia-smi &>/dev/null; then
    echo "ERROR: NVIDIA drivers not working!"
    echo "Please install drivers and reboot first:"
    echo "  sudo apt-get install ubuntu-drivers-common"
    echo "  sudo ubuntu-drivers install"
    echo "  sudo reboot"
    exit 1
fi

echo "NVIDIA driver verified:"
nvidia-smi

# Install CUDA 11.1 toolkit
echo "Installing CUDA 11.1 toolkit..."
if [ ! -f cuda-repo-ubuntu2004-11-1-local_11.1.0-455.23.05-1_amd64.deb ]; then
    wget https://developer.download.nvidia.com/compute/cuda/11.1.0/local_installers/cuda-repo-ubuntu2004-11-1-local_11.1.0-455.23.05-1_amd64.deb
fi
sudo dpkg -i cuda-repo-ubuntu2004-11-1-local_11.1.0-455.23.05-1_amd64.deb
sudo apt-key add /var/cuda-repo-ubuntu2004-11-1-local/7fa2af80.pub
sudo apt-get update
sudo apt-get -y install cuda-toolkit-11-1

# Set up environment
echo 'export PATH=/usr/local/cuda-11.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
export PATH=/usr/local/cuda-11.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:$LD_LIBRARY_PATH

# Verify CUDA
echo "Verifying CUDA 11.1..."
nvcc --version

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install PyTorch 1.10 with CUDA 11.1
echo "Installing PyTorch 1.10 + CUDA 11.1..."
pip3 install torch==1.10.0+cu111 torchvision==0.11.0+cu111 torchaudio==0.10.0 -f https://download.pytorch.org/whl/torch_stable.html

# Install NumPy (compatible version)
pip3 install "numpy<1.24"

# Install other Python dependencies
echo "Installing Python dependencies..."
pip3 install scipy pyyaml easydict tqdm tensorboard

# Install spconv for CUDA 11.1
echo "Installing spconv-cu111..."
pip3 install spconv-cu111

# Install Waymo evaluation
echo "Installing Waymo evaluation..."
pip3 install waymo-open-dataset-tf-2-5-0

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

# Set up Python path
export PYTHONPATH="${PYTHONPATH}:${HOME}/DetZero/detection:${HOME}/DetZero/utils:${HOME}/DetZero/tracking:${HOME}/DetZero/refining"
echo 'export PYTHONPATH="${PYTHONPATH}:${HOME}/DetZero/detection:${HOME}/DetZero/utils:${HOME}/DetZero/tracking:${HOME}/DetZero/refining"' >> ~/.bashrc

# Build CUDA extensions
echo "Building CUDA extensions..."
cd ~/DetZero/utils
python3 setup.py develop --user

cd ~/DetZero/detection
python3 setup.py develop --user

# Verify extensions
echo "Verifying CUDA extensions..."
python3 -c "from detzero_utils.ops.roiaware_pool3d import roiaware_pool3d_cuda; print('✓ Utils extensions loaded')"
python3 -c "from detzero_det.ops.iou3d_nms import iou3d_nms_utils; print('✓ Detection extensions loaded')"

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
echo "PyTorch Info:"
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
echo ""
echo "Disk Space:"
df -h ~
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Upload dataset (if not already done):"
echo "   gcloud compute scp --recurse /local/path/waymo_8k detzero-v100-training:~/ --zone=us-central1-a --project=detzeroaimob"
echo ""
echo "2. Start training in tmux:"
echo "   tmux new -s training"
echo "   cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh"
echo "   # Detach: Ctrl+B then D"
echo "   # Reattach: tmux attach -t training"
echo ""
echo "3. Monitor training:"
echo "   watch -n 1 nvidia-smi"
echo "   tail -f detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/log_train*.txt"
echo "=========================================="
