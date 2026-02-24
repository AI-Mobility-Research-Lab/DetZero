#!/bin/bash
# Google Cloud Platform A100 Setup Script with Auto Zone Selection
# Tries multiple zones until one succeeds

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
INSTANCE_NAME="${GCP_INSTANCE_NAME:-detzero-a100-training}"
MACHINE_TYPE="a2-highgpu-1g"
BOOT_DISK_SIZE="200GB"
DATA_DISK_SIZE="500GB"

# Zones to try (ordered by preference for East Coast)
ZONES=(
    "us-east1-b"        # South Carolina - closest to NYC
    "us-central1-a"     # Iowa - good availability
    "us-central1-b"     # Iowa
    "us-central1-c"     # Iowa
    "us-west1-b"        # Oregon
    "us-west4-b"        # Nevada
)

echo "=========================================="
echo "DetZero GCP A100 Auto Setup"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "Machine: $MACHINE_TYPE (1x A100 40GB)"
echo "Will try zones in order: ${ZONES[@]}"
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

# Try each zone until one succeeds
SUCCESS=false
for ZONE in "${ZONES[@]}"; do
    echo ""
    echo "=========================================="
    echo "Trying zone: $ZONE"
    echo "=========================================="
    
    # Try to create instance
    if gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --accelerator=type=nvidia-tesla-a100,count=1 \
        --boot-disk-size=$BOOT_DISK_SIZE \
        --boot-disk-type=pd-ssd \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --maintenance-policy=TERMINATE \
        --metadata=install-nvidia-driver=True \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --create-disk=name=${INSTANCE_NAME}-data,size=${DATA_DISK_SIZE},type=pd-ssd,auto-delete=yes \
        2>&1; then
        
        SUCCESS=true
        echo ""
        echo "=========================================="
        echo "✅ SUCCESS! Instance created in $ZONE"
        echo "=========================================="
        
        # Wait for instance to be ready
        sleep 30
        
        # Get instance IP
        INSTANCE_IP=$(gcloud compute instances describe $INSTANCE_NAME \
            --zone=$ZONE \
            --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
        
        echo ""
        echo "Instance: $INSTANCE_NAME"
        echo "Zone: $ZONE"
        echo "IP: $INSTANCE_IP"
        echo ""
        echo "Next steps:"
        echo "1. SSH: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
        echo "2. Run setup: bash /tmp/gcp_instance_setup.sh"
        echo "=========================================="
        
        # Copy setup script
        echo "Copying setup script to instance..."
        gcloud compute scp cloud/gcp_instance_setup.sh $INSTANCE_NAME:/tmp/ --zone=$ZONE
        
        # Save zone to file for later use
        echo "$ZONE" > /tmp/detzero_gcp_zone.txt
        echo ""
        echo "Zone saved to /tmp/detzero_gcp_zone.txt"
        
        break
    else
        echo "❌ Failed in $ZONE (likely resource exhausted)"
        echo "Trying next zone..."
    fi
done

if [ "$SUCCESS" = false ]; then
    echo ""
    echo "=========================================="
    echo "❌ ERROR: Could not create instance in any zone"
    echo "=========================================="
    echo "All zones exhausted. Possible solutions:"
    echo "1. Try again later (resources may become available)"
    echo "2. Use preemptible instance (add --preemptible flag)"
    echo "3. Try different regions (edit ZONES array in script)"
    echo "4. Request quota increase for A100 GPUs"
    echo "=========================================="
    exit 1
fi

echo ""
echo "Setup complete!"
