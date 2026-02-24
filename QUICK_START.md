# DetZero Quick Start Guide

## TL;DR - Get Training in 30 Minutes

```bash
# 1. Create V100 instance (2 min)
export GCP_PROJECT_ID="detzeroaimob"
bash cloud/gcp_setup_v100_standard.sh

# 2. SSH and setup (25 min)
gcloud compute ssh detzero-v100-training --zone=us-central1-a --project=detzeroaimob
wget https://raw.githubusercontent.com/AI-Mobility-Research-Lab/DetZero/main/cloud/gcp_instance_setup_pytorch110.sh
bash gcp_instance_setup_pytorch110.sh

# 3. Upload dataset (if needed - 30-60 min)
# From local machine:
gcloud compute scp --recurse /home/aimob/projects/OpenPCDet/data/waymo_8k detzero-v100-training:~/ --zone=us-central1-a --project=detzeroaimob

# 4. Start training (3 min)
tmux new -s training
cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh
# Detach: Ctrl+B, then D
```

## Critical Version Requirements

| Component | Version | Why |
|-----------|---------|-----|
| PyTorch | 1.10.0+cu111 | CUDA extensions built for this |
| CUDA | 11.1 | Matches PyTorch compilation |
| Python | 3.8-3.10 | Compatible with dependencies |
| Driver | 535+ | Modern GPU support |
| spconv | cu111 | Matches CUDA version |

**DO NOT USE**: PyTorch 2.x, CUDA 12.x (requires code refactoring)

## Training Specs

- **GPU**: V100 16GB
- **Batch Size**: 4
- **Epochs**: 30
- **Time**: ~4-5 hours
- **Cost**: ~$12
- **Expected mAPH L2**: ~76.24

## Monitoring

```bash
# GPU usage
watch -n 1 nvidia-smi

# Training logs
tail -f ~/DetZero/detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/log_train*.txt

# Reattach to training
tmux attach -t training
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `nvidia-smi` fails | Install drivers: `sudo ubuntu-drivers install && sudo reboot` |
| CUDA version mismatch | Use CUDA 11.1, not 12.x |
| THC/THC.h not found | Use PyTorch 1.10, not 2.x |
| OOM errors | Reduce batch_size or use larger GPU |
| Module not found | Check PYTHONPATH in ~/.bashrc |

## Files Reference

- **Setup**: `cloud/gcp_instance_setup_pytorch110.sh`
- **Training**: `scripts/train_8k_waymo_v100.sh`
- **Requirements**: `requirements-cuda111.txt`
- **Full Guide**: `docs/INSTALLATION.md`
- **Lessons**: `docs/LESSONS_LEARNED.md`

## Cost Breakdown

- V100: $2.48/hour
- Training: 4-5 hours = $10-12
- Storage: 150GB = $0.04/hour
- **Total**: ~$12-15 per training run

## Next Steps After Training

1. Check results: `~/DetZero/detection/output/waymo_8k/centerpoint_1sweep_8k/waymo_8k_v100/`
2. Evaluate: Follow `detection/README.md`
3. Visualize: Use `daemon/visualizer.py`
4. Stop instance: `gcloud compute instances stop detzero-v100-training --zone=us-central1-a`

## Support

- Issues: See `docs/LESSONS_LEARNED.md`
- Original docs: `docs/INSTALL.md`
- Paper: https://arxiv.org/abs/2306.06023
