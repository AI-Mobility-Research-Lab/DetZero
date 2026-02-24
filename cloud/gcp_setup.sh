#!/bin/bash
# Google Cloud Platform A100 Setup Script for DetZero Training

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE_NAME="${GCP_INSTANCE_NAME:-detzero-a100-training}"
MACHINE_TYPE="a2-highgpu-1g"  # 1x A100 40GB, 12 vCPUs, 85 GB RAM
BOOT_DISK_SIZE="200GB"
DATA_DISK_SIZE="500GB"

echo "=========================================="
echo "DetZero GCP A100 Setup"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"
echo "Instance: $INSTANCE_NAME"
echo "Machine: $MACHINE_TYPE (1x A100 40GB)"
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

# Create instance with A100 GPU
echo "Creating A100 instance..."
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --accelerator=type=nvidia-tesla-a100,count=1 \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2004-lts \
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
echo "IP: $INSTANCE_IP"
echo "SSH: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "Next steps:"
echo "1. SSH into instance: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo "2. Run setup script: bash /tmp/gcp_instance_setup.sh"
echo "3. Upload data and start training"
echo "=========================================="

# Copy setup script to instance
echo "Copying setup script to instance..."
gcloud compute scp cloud/gcp_instance_setup.sh $INSTANCE_NAME:/tmp/ --zone=$ZONE

echo ""
echo "Setup complete! SSH into the instance to continue."
