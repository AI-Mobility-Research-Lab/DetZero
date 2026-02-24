#!/bin/bash
# Run detection in background with nohup

echo "Starting 8K detection in background..."
echo "Logs will be written to: logs/detection_8k_nohup.out"
echo ""

# Create logs directory
mkdir -p logs

nohup python3 scripts/8k_pipeline/run_detection_8k.py \
    --cfg_file detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --workers 4 \
    --output_dir output_8k/detection \
    --split val \
    > logs/detection_8k_nohup.out 2>&1 &

PID=$!
echo "Detection started with PID: $PID"
echo $PID > logs/detection_8k.pid
echo ""
echo "📊 Monitor progress:"
echo "  tail -f logs/detection_8k.log          # Detailed logs"
echo "  tail -f logs/detection_8k_nohup.out    # Console output"
echo ""
echo "🔍 Check if still running:"
echo "  ps -p $PID"
echo "  cat logs/detection_8k.pid | xargs ps -p"
echo ""
echo "⏹️  Stop detection:"
echo "  kill $PID"
echo "  kill \$(cat logs/detection_8k.pid)"
echo ""
echo "✅ Detection running in background!"
echo ""
