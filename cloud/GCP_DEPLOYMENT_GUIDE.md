# Google Cloud A100 Deployment Guide

## Overview

Deploy DetZero training on Google Cloud A100 GPU for faster training:
- **Local (RTX 4060 8GB)**: ~12.5 hours, batch_size=1
- **GCP A100 (40GB)**: ~2-3 hours, batch_size=8 (4-5x faster)

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **GPU Quota**: Request A100 quota in your GCP project
   - Go to: IAM & Admin → Quotas
   - Search for "A100 GPUs"
   - Request quota increase if needed

## Cost Estimate

**A100 Instance (a2-highgpu-1g)**:
- 1x A100 40GB GPU
- 12 vCPUs, 85 GB RAM
- Cost: ~$3.67/hour (us-central1)
- Training time: ~2-3 hours
- **Total cost: ~$7-11 per training run**

## Quick Start

### 1. Configure GCP Project

```bash
# Set your project ID and zone
export GCP_PROJECT_ID="your-project-id"
export GCP_ZONE="us-east4-c"  # Best for NYC - Northern Virginia

# Login to GCP
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
```

### 2. Create A100 Instance

```bash
# Run setup script
cd ~/projects/DetZero
bash cloud/gcp_setup.sh
```

This will:
- Create A100 instance with NVIDIA drivers
- Attach 200GB boot disk + 500GB data disk
- Install required software
- Copy setup scripts

### 3. SSH into Instance

```bash
gcloud compute ssh detzero-a100-training --zone=$GCP_ZONE
```

### 4. Setup Instance

```bash
# Run instance setup (already copied by gcp_setup.sh)
bash /tmp/gcp_instance_setup.sh
```

This will:
- Install CUDA, PyTorch, dependencies
- Clone DetZero repository
- Build CUDA extensions
- Setup data directory

### 5. Upload Dataset

**Option A: From Google Cloud Storage**
```bash
# Upload to GCS first (from local machine)
gsutil -m cp -r /home/aimob/projects/OpenPCDet/data/waymo_8k gs://your-bucket/

# Download on instance
gsutil -m rsync -r gs://your-bucket/waymo_8k /mnt/data/
```

**Option B: Direct SCP (slower)**
```bash
# From local machine
gcloud compute scp --recurse \
    /home/aimob/projects/OpenPCDet/data/waymo_8k \
    detzero-a100-training:/mnt/data/ \
    --zone=$GCP_ZONE
```

### 6. Start Training

```bash
# On the instance
cd ~/DetZero
tmux new-session -s training
bash scripts/train_8k_waymo_a100.sh
# Press Ctrl+B then D to detach
```

### 7. Monitor Training

```bash
# Attach to training session
tmux attach -t training

# Check GPU usage
watch -n 1 nvidia-smi

# Check training log
tail -f detection/output/cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k_a100/log_train_*.txt
```

### 8. Download Results

```bash
# From local machine
gcloud compute scp --recurse \
    detzero-a100-training:~/DetZero/detection/output/cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k_a100 \
    ./results/ \
    --zone=$GCP_ZONE
```

### 9. Stop/Delete Instance

```bash
# Stop instance (keeps disk, can restart later)
gcloud compute instances stop detzero-a100-training --zone=$GCP_ZONE

# Delete instance (removes everything, saves cost)
gcloud compute instances delete detzero-a100-training --zone=$GCP_ZONE
```

## A100 Training Configuration

The A100 training script uses optimized settings:

```bash
BATCH_SIZE=8        # vs 1 on RTX 4060
WORKERS=8           # vs 1 on RTX 4060
TF32 enabled        # Faster training on A100
```

**Expected Performance**:
- Speed: ~15-20 it/s (vs 4.7 it/s on RTX 4060)
- Memory: ~25 GB / 40 GB
- Training time: ~2-3 hours (vs 12.5 hours)

## Cost Optimization Tips

### 1. Use Preemptible Instances (70% cheaper)
```bash
# Add --preemptible flag to gcp_setup.sh
gcloud compute instances create ... --preemptible
```
- Cost: ~$1.10/hour (vs $3.67/hour)
- Risk: Can be terminated anytime (save checkpoints frequently)

### 2. Use Spot VMs (similar to preemptible)
```bash
gcloud compute instances create ... --provisioning-model=SPOT
```

### 3. Stop Instance When Not Training
```bash
# Stop (keeps disk, ~$0.04/hour for storage)
gcloud compute instances stop detzero-a100-training --zone=$GCP_ZONE

# Start when needed
gcloud compute instances start detzero-a100-training --zone=$GCP_ZONE
```

### 4. Choose Optimal Zone

**For New York / East Coast**:

| Zone | Location | A100 Price/hr | Latency | Recommendation |
|------|----------|---------------|---------|----------------|
| **us-east4** | Northern Virginia | **$3.67** | ~10ms | ✅ **Best choice** |
| us-east1 | South Carolina | $3.67 | ~20ms | Good |
| northamerica-northeast1 | Montreal | $4.03 | ~15ms | More expensive |
| northamerica-northeast2 | Toronto | $4.03 | ~20ms | More expensive |
| us-central1 | Iowa | $3.67 | ~30ms | Farther |

**Recommendation for NYC**: Use **us-east4** (Northern Virginia)
- Lowest price: $3.67/hour
- Best latency: ~10ms from NYC
- Good A100 availability

Check current pricing: https://cloud.google.com/compute/gpus-pricing

## Troubleshooting

### GPU Quota Error
```
ERROR: Quota 'NVIDIA_A100_GPUS' exceeded
```
**Solution**: Request quota increase in GCP Console → IAM & Admin → Quotas

### Out of Memory on A100
If training still OOMs (unlikely with 40GB):
```bash
# Reduce batch size in scripts/train_8k_waymo_a100.sh
BATCH_SIZE=4  # or 2
```

### SSH Connection Issues
```bash
# Add firewall rule for SSH
gcloud compute firewall-rules create allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0
```

### Data Transfer Too Slow
Use Google Cloud Storage for faster transfers:
1. Upload to GCS bucket first
2. Use `gsutil -m` for parallel transfer
3. Download on instance (fast internal network)

## Monitoring and Alerts

### Setup Monitoring (Optional)

```bash
# On instance, setup the monitor with WhatsApp/Telegram
cd ~/DetZero
# Edit scripts/monitor_training.sh with your notification method
tmux new-session -d -s monitor
tmux send-keys -t monitor "bash scripts/monitor_training.sh" C-m
```

### GCP Monitoring Dashboard

View metrics in GCP Console:
- Compute Engine → VM instances → detzero-a100-training
- Monitoring → Dashboards → Create custom dashboard
- Add GPU utilization, memory, temperature metrics

## Comparison: Local vs GCP A100

| Metric | RTX 4060 (Local) | A100 (GCP) |
|--------|------------------|------------|
| VRAM | 8 GB | 40 GB |
| Batch Size | 1 | 8 |
| Speed | 4.7 it/s | 15-20 it/s |
| Training Time | 12.5 hours | 2-3 hours |
| Cost | Free (electricity) | $7-11 |
| Reliability | Can crash (OOM) | Stable |

## Next Steps After Training

1. Download trained model
2. Run evaluation on validation set
3. Run tracking pipeline
4. Run refinement pipeline
5. Visualize results

See main README for post-training steps.

## Support

- GCP Documentation: https://cloud.google.com/compute/docs
- A100 Specs: https://www.nvidia.com/en-us/data-center/a100/
- DetZero Issues: https://github.com/AI-Mobility-Research-Lab/DetZero/issues
