#!/bin/bash
# Run detection in screen session

SESSION_NAME="detzero_detection_8k"

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo "❌ screen is not installed"
    echo "Install with: sudo apt-get install screen"
    exit 1
fi

# Check if session already exists
if screen -list | grep -q "$SESSION_NAME"; then
    echo "⚠️  Session '$SESSION_NAME' already exists"
    echo ""
    echo "Options:"
    echo "  1. Attach to existing session: screen -r $SESSION_NAME"
    echo "  2. Kill existing session: screen -X -S $SESSION_NAME quit"
    echo "  3. Use a different session name"
    exit 1
fi

echo "Starting detection in screen session: $SESSION_NAME"
echo ""

# Create new screen session and run detection
screen -dmS $SESSION_NAME bash -c "python3 run_detection_8k.py \
    --cfg_file detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --workers 4 \
    --output_dir output_8k/detection \
    --split val; \
    echo ''; \
    echo 'Detection complete! Press any key to exit...'; \
    read"

echo "✅ Detection started in screen session: $SESSION_NAME"
echo ""
echo "Commands:"
echo "  Attach to session:  screen -r $SESSION_NAME"
echo "  Detach from session: Press Ctrl+A, then D"
echo "  List sessions:      screen -ls"
echo "  Kill session:       screen -X -S $SESSION_NAME quit"
echo ""
echo "The session will keep running even if you disconnect from SSH"
echo ""
