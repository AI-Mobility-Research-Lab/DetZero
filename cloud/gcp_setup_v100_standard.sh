#!/bin/bash
# Create V100 instance using standard persistent disk (no SSD quota issues)

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-detzeroaimob}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE_NAME="detzero-v100-training"
MACHINE_TYPE="n1-highmem-8"
GPU_TYPE="nvidia-tesla-v100"
GPU_COUNT=1

# Use Ubuntu 22.04 image (we'll install drivers via script)
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

# Use standard persistent disk (no SSD quota needed)
BOOT_DISK_SIZE="150GB"
BOOT_DISK_TYPE="pd-standard"

echo "=========================================="
echo "DetZero GCP V100 Setup"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"
echo "Instance: $INSTANCE_NAME"
echo "Machine: $MACHINE_TYPE + ${GPU_COUNT}x V100 16GB"
echo "Image: Ubuntu 22.04 LTS"
echo "Disk: Standard Persistent Disk (no SSD quota)"
echo "Cost: ~\$2.48/hour"
echo "=========================================="

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Delete existing instance if it exists
if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
    echo "Deleting existing instance..."
    gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE --quiet
fi

# Create instance with Ubuntu 22.04
echo "Creating V100 instance..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --accelerator=type=$GPU_TYPE,count=$GPU_COUNT \
    --maintenance-policy=TERMINATE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=$BOOT_DISK_TYPE \
    --metadata="install-nvidia-driver=True" \
    --scopes=cloud-platform

echo ""
echo "=========================================="
echo "Instance Created Successfully!"
echo "=========================================="
echo "Waiting 90 seconds for instance to boot and install drivers..."
sleep 90

echo ""
echo "Uploading setup script..."
gcloud compute scp --zone=$ZONE \
    cloud/gcp_instance_setup_working.sh \
    $INSTANCE_NAME:/tmp/gcp_instance_setup.sh

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. SSH into instance:"
echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "2. Run setup script:"
echo "   bash /tmp/gcp_instance_setup.sh"
echo ""
echo "3. Upload dataset (from local machine):"
echo "   gcloud compute scp --recurse /home/aimob/projects/OpenPCDet/data/waymo_8k $INSTANCE_NAME:~/ --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "4. Start training:"
echo "   cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh"
echo "=========================================="
