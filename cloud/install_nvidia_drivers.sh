#!/bin/bash
# Quick script to install NVIDIA drivers on GCP V100 instance

set -e

echo "=========================================="
echo "Installing NVIDIA Drivers and CUDA"
echo "=========================================="

# Download CUDA repository key
echo "Adding NVIDIA repository..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# Install CUDA (includes NVIDIA drivers)
echo "Installing CUDA 12.1 (this will take 5-10 minutes)..."
sudo apt-get -y install cuda-12-1

# Set up environment variables
echo "Configuring environment..."
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc

# Load environment for current session
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo "Verifying GPU..."
/usr/bin/nvidia-smi

echo ""
echo "CUDA version:"
/usr/local/cuda-12.1/bin/nvcc --version

echo ""
echo "=========================================="
echo "Next: Run the full setup script"
echo "bash /tmp/gcp_instance_setup.sh"
echo "=========================================="
