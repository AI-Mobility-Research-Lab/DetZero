#!/bin/bash
# One-command script to fix setup and start training

echo "=========================================="
echo "DetZero Training - Complete Setup & Start"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Fix the conda environment"
echo "2. Generate pickle files with correct paths"
echo "3. Start training in tmux"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

cd ~/DetZero

# Step 1: Fix setup
echo ""
echo "Step 1: Fixing setup..."
bash fix_training_setup.sh

# Check if pickle files were generated successfully
if [ ! -f ~/DetZero/data/waymo_8k/waymo_infos_train.pkl ]; then
    echo ""
    echo "ERROR: Pickle files not generated!"
    echo "Please check the output above for errors."
    exit 1
fi

# Verify pickle files have data
train_samples=$(python3 -c "import pickle; data=pickle.load(open('/home/aimob/DetZero/data/waymo_8k/waymo_infos_train.pkl','rb')); print(len(data))" 2>/dev/null)

if [ "$train_samples" = "0" ] || [ -z "$train_samples" ]; then
    echo ""
    echo "ERROR: Training pickle file is empty or invalid!"
    echo "Please check the dataset at ~/waymo_8k/waymo_processed_data/"
    exit 1
fi

echo ""
echo "✓ Setup complete! Found $train_samples training samples"
echo ""

# Step 2: Start training in tmux
echo "Step 2: Starting training in tmux..."
echo ""
echo "Training will start in a tmux session named 'training'"
echo "You can detach with: Ctrl+B, then D"
echo "You can reattach with: tmux attach -t training"
echo ""
read -p "Press Enter to start training..."

# Kill existing training session if it exists
tmux kill-session -t training 2>/dev/null || true

# Start new training session
tmux new -s training -d "cd ~/DetZero && bash scripts/train_8k_waymo_v100.sh; echo 'Training finished! Press Enter to close.'; read"

echo ""
echo "=========================================="
echo "Training started in tmux!"
echo "=========================================="
echo ""
echo "To view training progress:"
echo "  tmux attach -t training"
echo ""
echo "To detach (keep training running):"
echo "  Press Ctrl+B, then D"
echo ""
echo "Expected training time: ~4-5 hours"
echo ""
echo "When done, stop the instance to save costs:"
echo "  gcloud compute instances stop detzero-v100-training \\"
echo "      --zone=us-central1-a --project=detzeroaimob"
echo ""
echo "Attaching to training session in 3 seconds..."
sleep 3
tmux attach -t training
