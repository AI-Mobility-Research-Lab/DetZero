#!/bin/bash
# Google Cloud Platform V100 Setup Script (Alternative to A100)
# V100 is more available and cheaper, still much faster than RTX 4060

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-detzeroaimob}"  # Your actual project ID
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE_NAME="${GCP_INSTANCE_NAME:-detzero-v100-training}"
MACHINE_TYPE="n1-highmem-8"  # 8 vCPUs, 52 GB RAM
GPU_TYPE="nvidia-tesla-v100"
GPU_COUNT=1
BOOT_DISK_SIZE="100GB"  # Reduced from 200GB
DATA_DISK_SIZE="200GB"  # Reduced from 500GB (total: 300GB < 500GB limit)

echo "=========================================="
echo "DetZero GCP V100 Setup"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"
echo "Instance: $INSTANCE_NAME"
echo "Machine: $MACHINE_TYPE + 1x V100 16GB"
echo "Cost: ~$2.48/hour (vs $3.67 for A100)"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Create instance with V100 GPU
echo "Creating V100 instance..."
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --accelerator=type=$GPU_TYPE,count=$GPU_COUNT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --maintenance-policy=TERMINATE \
    --metadata=install-nvidia-driver=True \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --create-disk=name=${INSTANCE_NAME}-data,size=${DATA_DISK_SIZE},type=pd-ssd,auto-delete=yes

echo ""
echo "Instance created! Waiting for it to be ready..."
sleep 30

# Get instance IP
INSTANCE_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo "=========================================="
echo "Instance Ready!"
echo "=========================================="
echo "Instance: $INSTANCE_NAME"
echo "Zone: $ZONE"
echo "IP: $INSTANCE_IP"
echo "GPU: V100 16GB"
echo "Cost: ~$2.48/hour"
echo "Training time: ~4-5 hours (vs 2-3 hours on A100)"
echo ""
echo "Next steps:"
echo "1. SSH: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo "2. Run setup: bash /tmp/gcp_instance_setup.sh"
echo "3. Start training: bash scripts/train_8k_waymo_v100.sh"
echo "=========================================="

# Copy setup script to instance
echo "Copying setup script to instance..."
gcloud compute scp cloud/gcp_instance_setup.sh $INSTANCE_NAME:/tmp/ --zone=$ZONE

echo ""
echo "Setup complete! SSH into the instance to continue."
