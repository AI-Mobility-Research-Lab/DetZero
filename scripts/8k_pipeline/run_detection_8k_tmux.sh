#!/bin/bash
# Run detection in tmux session

SESSION_NAME="detzero_detection_8k"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux is not installed"
    echo "Install with: sudo apt-get install tmux"
    exit 1
fi

# Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "⚠️  Session '$SESSION_NAME' already exists"
    echo ""
    echo "Options:"
    echo "  1. Attach to existing session: tmux attach -t $SESSION_NAME"
    echo "  2. Kill existing session: tmux kill-session -t $SESSION_NAME"
    echo "  3. Use a different session name"
    exit 1
fi

echo "Starting detection in tmux session: $SESSION_NAME"
echo ""

# Create new tmux session and run detection
tmux new-session -d -s $SESSION_NAME "python3 run_detection_8k.py \
    --cfg_file detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --workers 4 \
    --output_dir output_8k/detection \
    --split val; \
    echo ''; \
    echo 'Detection complete! Press any key to exit...'; \
    read"

echo "✅ Detection started in tmux session: $SESSION_NAME"
echo ""
echo "Commands:"
echo "  Attach to session:  tmux attach -t $SESSION_NAME"
echo "  Detach from session: Press Ctrl+B, then D"
echo "  List sessions:      tmux ls"
echo "  Kill session:       tmux kill-session -t $SESSION_NAME"
echo ""
echo "The session will keep running even if you disconnect from SSH"
echo ""
