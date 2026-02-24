#!/bin/bash
# Run OpenPCDet test script directly

echo "Running OpenPCDet detection on 8K dataset..."
echo ""

cd /home/aimob/projects/OpenPCDet

python3 tools/test.py \
    --cfg_file tools/cfgs/nuscenes_custom_models/centerpoint_8k.yaml \
    --ckpt output/cfgs/nuscenes_custom_models/centerpoint_8k/centerpoint_8k_20260213_191157/ckpt/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --workers 4

echo ""
echo "Detection complete!"
echo "Results saved in: output/cfgs/nuscenes_custom_models/centerpoint_8k/centerpoint_8k_20260213_191157/eval/"
