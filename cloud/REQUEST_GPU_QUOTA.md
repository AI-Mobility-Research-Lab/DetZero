# How to Request GPU Quota in Google Cloud

## Problem

```
ERROR: Quota 'GPUS_ALL_REGIONS' exceeded. Limit: 0.0 globally.
```

Your GCP project has no GPU quota allocated. You need to request a quota increase.

## Solution: Request GPU Quota

### Step 1: Go to Quotas Page

1. Open Google Cloud Console: https://console.cloud.google.com
2. Select your project: `detzeroaimob`
3. Go to: **IAM & Admin** → **Quotas**
4. Or direct link: https://console.cloud.google.com/iam-admin/quotas

### Step 2: Filter for GPU Quotas

In the Quotas page:
1. Click **Filter** button
2. Add filter: **Service** = `Compute Engine API`
3. Add filter: **Dimensions** = `global`
4. Search for: `GPUS_ALL_REGIONS`

### Step 3: Request Quota Increase

1. Check the box next to `GPUS_ALL_REGIONS`
2. Click **EDIT QUOTAS** button at the top
3. Fill in the form:
   - **New limit**: `1` (for 1 GPU)
   - **Request description**: 
     ```
     Requesting 1 GPU quota for machine learning training workload.
     Will be using V100 or A100 GPU for deep learning model training.
     Estimated usage: 4-5 hours per training run, 1-2 runs per week.
     ```
4. Click **SUBMIT REQUEST**

### Step 4: Wait for Approval

- **Typical approval time**: 2-48 hours
- **Email notification**: You'll receive an email when approved
- **Check status**: Go back to Quotas page to see current limit

### Alternative: Request Specific GPU Quota

If you want to request specific GPU types:

**For V100:**
1. Filter for: `NVIDIA_V100_GPUS`
2. Request limit: `1`

**For A100:**
1. Filter for: `NVIDIA_A100_GPUS`
2. Request limit: `1`

## Recommended Quota Request

For your use case, request:

| Quota | Recommended Limit | Reason |
|-------|-------------------|--------|
| **GPUS_ALL_REGIONS** | 1 | Allows any GPU type |
| **NVIDIA_V100_GPUS** | 1 | Better availability |
| **NVIDIA_A100_GPUS** | 1 | Faster training (if available) |

## Tips for Faster Approval

1. **Use a business email** if possible (not Gmail)
2. **Provide detailed justification**:
   - Specific use case (ML training)
   - Estimated usage hours
   - Why you need GPU (vs CPU)
3. **Start small**: Request 1 GPU first, can increase later
4. **Verify billing**: Ensure billing is enabled on your project

## While Waiting for Approval

### Option 1: Continue Local Training ✅

Your local training is already running and stable:
- Progress: ~40% of epoch 1
- ETA: ~12.5 hours total
- Cost: Free
- **Recommendation**: Let it finish

### Option 2: Use Google Colab (Free)

Google Colab provides free GPU access:
1. Go to: https://colab.research.google.com
2. Runtime → Change runtime type → GPU (T4)
3. Upload your code and data
4. Run training

**Limitations:**
- 12-hour session limit
- May disconnect randomly
- Slower than V100/A100

### Option 3: Try Other Cloud Providers

**AWS:**
- Usually has better GPU availability
- Similar pricing to GCP
- Requires AWS account setup

**Azure:**
- Good GPU availability
- Similar pricing
- Requires Azure account setup

## Check Quota Status

```bash
# Check current GPU quota
gcloud compute project-info describe --project=detzeroaimob \
    --format="table(quotas.metric,quotas.limit,quotas.usage)"

# Or use gcloud command
gcloud compute regions describe us-central1 \
    --format="table(quotas.metric,quotas.limit,quotas.usage)"
```

## After Quota Approval

Once your quota is approved:

```bash
# Verify quota
gcloud compute project-info describe --project=detzeroaimob | grep -A 2 GPUS_ALL_REGIONS

# Create V100 instance
bash cloud/gcp_setup_v100.sh
```

## Common Issues

### "Quota increase request denied"

**Reasons:**
- New GCP account (< 30 days old)
- No billing history
- Insufficient justification

**Solution:**
- Wait 30 days and try again
- Add payment method and make small purchases
- Provide more detailed justification

### "Quota approved but still getting error"

**Solution:**
- Wait 5-10 minutes for quota to propagate
- Try different zone
- Clear gcloud cache: `gcloud config configurations list`

## Support

- GCP Quota Documentation: https://cloud.google.com/compute/quotas
- GCP Support: https://cloud.google.com/support
- Community Support: https://stackoverflow.com/questions/tagged/google-cloud-platform

## Summary

1. ✅ Request GPU quota in GCP Console (2-48 hours)
2. ⏳ Continue local training while waiting
3. 🚀 Use V100 once quota approved

Your local training is already 40% done and stable - let it finish while waiting for quota approval!
