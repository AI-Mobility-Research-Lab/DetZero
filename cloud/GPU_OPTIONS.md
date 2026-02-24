# GCP GPU Options for DetZero Training

## Problem: A100 Unavailability

A100 GPUs are in very high demand and often show `ZONE_RESOURCE_POOL_EXHAUSTED` errors. Here are your options:

## Option 1: V100 (Recommended Alternative) ✅

**Specs:**
- GPU: NVIDIA Tesla V100 16GB
- Cost: ~$2.48/hour
- Availability: ✅ Much better than A100
- Training time: ~4-5 hours

**Setup:**
```bash
bash cloud/gcp_setup_v100.sh
```

**Pros:**
- ✅ Much more available
- ✅ 32% cheaper than A100 ($2.48 vs $3.67/hour)
- ✅ Still 3x faster than RTX 4060
- ✅ 16GB VRAM (enough for batch_size=4)

**Cons:**
- ⚠️ Slower than A100 (4-5 hours vs 2-3 hours)

## Option 2: Wait for A100

**Setup:**
```bash
# Try auto script periodically
bash cloud/gcp_setup_auto.sh
```

**Tips:**
- Try during off-peak hours (late night/early morning US time)
- Try weekends
- Set up a cron job to retry automatically

## Option 3: Use Preemptible A100 (70% cheaper)

Preemptible instances are much more available but can be terminated anytime.

**Setup:**
Edit `cloud/gcp_setup.sh` and add `--preemptible`:
```bash
gcloud compute instances create ... \
    --preemptible \
    --max-run-duration=3h \
    ...
```

**Pros:**
- ✅ Better availability
- ✅ Only $1.10/hour (vs $3.67)
- ✅ Can save checkpoints and resume

**Cons:**
- ⚠️ Can be terminated anytime (save checkpoints frequently)
- ⚠️ Max 24 hours runtime

## Option 4: Continue on Local RTX 4060

Your local training is already running and stable.

**Current Status:**
- Progress: ~40% of epoch 1
- ETA: ~12.5 hours total
- Cost: Free (electricity only)
- Reliability: Stable with memory optimizations

**Recommendation:** Let it finish locally while trying to get cloud GPU for future runs.

## Comparison Table

| Option | GPU | VRAM | Cost/hr | Training Time | Availability | Total Cost |
|--------|-----|------|---------|---------------|--------------|------------|
| **Local** | RTX 4060 | 8GB | Free | 12.5 hours | ✅ Always | $0 |
| **V100** | Tesla V100 | 16GB | $2.48 | 4-5 hours | ✅ Good | $10-12 |
| **A100** | Tesla A100 | 40GB | $3.67 | 2-3 hours | ❌ Exhausted | $7-11 |
| **A100 Preemptible** | Tesla A100 | 40GB | $1.10 | 2-3 hours | ⚠️ Better | $2-3 |

## Recommended Strategy

### For This Training Run:
1. **Continue local training** - It's already 40% done and stable
2. **Try V100 for next run** - More available, still much faster

### For Future Runs:
1. **First choice: V100** - Best balance of availability, cost, and speed
2. **Second choice: Preemptible A100** - If you can handle interruptions
3. **Third choice: Wait for A100** - Try during off-peak hours

## V100 Quick Start

```bash
# 1. Create V100 instance
bash cloud/gcp_setup_v100.sh

# 2. SSH into instance
gcloud compute ssh detzero-v100-training --zone=us-central1-a

# 3. Setup instance
bash /tmp/gcp_instance_setup.sh

# 4. Upload data
gsutil -m rsync -r gs://your-bucket/waymo_8k /mnt/data/

# 5. Start training
cd ~/DetZero
bash scripts/train_8k_waymo_v100.sh
```

## Cost Comparison for 30 Epochs

| GPU | Time | Cost/hr | Total Cost |
|-----|------|---------|------------|
| RTX 4060 (Local) | 12.5 hrs | $0 | **$0** |
| V100 (GCP) | 4-5 hrs | $2.48 | **$10-12** |
| A100 (GCP) | 2-3 hrs | $3.67 | **$7-11** |
| A100 Preemptible | 2-3 hrs | $1.10 | **$2-3** |

## Monitoring A100 Availability

Check availability in real-time:
```bash
# Check all zones
for zone in us-east1-b us-central1-a us-central1-b us-west1-b; do
    echo "Checking $zone..."
    gcloud compute instances create test-a100 \
        --zone=$zone \
        --machine-type=a2-highgpu-1g \
        --accelerator=type=nvidia-tesla-a100,count=1 \
        --dry-run 2>&1 | grep -q "EXHAUSTED" && echo "❌ Exhausted" || echo "✅ Available"
done
```

## Support

- GCP GPU Pricing: https://cloud.google.com/compute/gpus-pricing
- Resource Availability: https://cloud.google.com/compute/docs/resource-error
- DetZero Issues: https://github.com/AI-Mobility-Research-Lab/DetZero/issues
