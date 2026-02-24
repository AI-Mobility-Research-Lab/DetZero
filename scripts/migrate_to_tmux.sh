#!/bin/bash
# Migrate current training to tmux session

echo "=== Migrating Training to tmux ==="
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux is not installed. Installing..."
    sudo apt install tmux -y
fi

# Check if training is running
TRAIN_PID=$(ps aux | grep "python tools/train.py" | grep -v grep | head -1 | awk '{print $2}')

if [ -z "$TRAIN_PID" ]; then
    echo "✅ No training process found. Starting fresh in tmux..."
else
    echo "⚠️  Found training process (PID: $TRAIN_PID)"
    echo "   This will be stopped and restarted in tmux."
    read -p "   Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    
    echo "Stopping current training..."
    kill $TRAIN_PID
    sleep 2
fi

# Check if tmux session already exists
if tmux has-session -t training 2>/dev/null; then
    echo "⚠️  tmux session 'training' already exists"
    read -p "   Kill existing session and create new one? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t training
    else
        echo "Cancelled. Use 'tmux attach -t training' to reconnect."
        exit 1
    fi
fi

echo ""
echo "Creating tmux session 'training'..."
echo ""
echo "Commands to use after training starts:"
echo "  - Detach from tmux: Ctrl+B, then D"
echo "  - Reattach later: tmux attach -t training"
echo ""
echo "Starting training in 3 seconds..."
sleep 3

# Create tmux session and start training
tmux new-session -d -s training "cd /home/aimob/projects/DetZero && ./scripts/train_8k_waymo.sh"

echo ""
echo "✅ Training started in tmux session 'training'"
echo ""
echo "To view training progress:"
echo "  tmux attach -t training"
echo ""
echo "To check if it's running:"
echo "  tmux ls"
echo "  ps aux | grep train.py"
echo ""
echo "Training is now persistent and will survive SSH disconnections!"
