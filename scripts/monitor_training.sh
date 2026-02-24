#!/bin/bash
# Monitor training process and send Telegram alert if it crashes

# Configuration
TRAINING_PID_FILE="/tmp/detzero_training.pid"
CHECK_INTERVAL=60  # Check every 60 seconds

# IMPORTANT: Set your Telegram chat ID here
# To get your chat ID:
# 1. Start a chat with your OpenClaw bot on Telegram
# 2. Send any message to the bot
# 3. Run: openclaw directory peers list --channel telegram
# 4. Find your chat ID and set it below (e.g., "123456789" or "-100123456789" for groups)
TELEGRAM_TARGET=""  # Set your chat ID here (e.g., "123456789")

if [ -z "$TELEGRAM_TARGET" ]; then
    echo "✗ ERROR: TELEGRAM_TARGET not set!"
    echo "Please edit this script and set your Telegram chat ID"
    echo "See instructions in the script header"
    exit 1
fi

# Get the current training PID
get_training_pid() {
    ps aux | grep "python tools/train.py" | grep -v grep | grep "centerpoint_1sweep_8k" | awk '{print $2}' | head -1
}

# Check if process is running
is_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    kill -0 "$pid" 2>/dev/null
    return $?
}

# Send Telegram notification
send_telegram() {
    local message="$1"
    openclaw message send \
        --channel telegram \
        --target "$TELEGRAM_TARGET" \
        --message "$message" \
        2>&1 | grep -q "success" && echo "✓ Telegram notification sent" || echo "✗ Failed to send Telegram notification"
}

# Get GPU status
get_gpu_status() {
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A"
}

# Main monitoring loop
echo "=========================================="
echo "DetZero Training Monitor"
echo "=========================================="
echo "Telegram target: $TELEGRAM_TARGET"
echo "Check interval: ${CHECK_INTERVAL}s"
echo "=========================================="

# Find initial PID
CURRENT_PID=$(get_training_pid)

if [ -z "$CURRENT_PID" ]; then
    echo "✗ No training process found!"
    send_telegram "⚠️ DetZero Training Monitor: No training process found at startup"
    exit 1
fi

echo "✓ Found training process: PID $CURRENT_PID"
echo "$CURRENT_PID" > "$TRAINING_PID_FILE"

# Send startup notification
GPU_STATUS=$(get_gpu_status)
send_telegram "🚀 DetZero Training Monitor Started

PID: $CURRENT_PID
GPU: $GPU_STATUS
Checking every ${CHECK_INTERVAL}s"

# Monitor loop
LAST_CHECK=$(date +%s)
CHECK_COUNT=0

while true; do
    sleep "$CHECK_INTERVAL"
    
    CHECK_COUNT=$((CHECK_COUNT + 1))
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - LAST_CHECK))
    
    # Check if process is still running
    if ! is_running "$CURRENT_PID"; then
        echo ""
        echo "=========================================="
        echo "✗ TRAINING PROCESS CRASHED!"
        echo "=========================================="
        echo "Time: $(date)"
        echo "PID: $CURRENT_PID"
        echo "Checks performed: $CHECK_COUNT"
        
        # Get latest log
        LATEST_LOG=$(ls -t detection/output/cfgs/det_model_cfgs/centerpoint_1sweep_8k/waymo_8k/log_train_*.txt 2>/dev/null | head -1)
        
        if [ -n "$LATEST_LOG" ]; then
            LAST_LINES=$(tail -20 "$LATEST_LOG" | grep -E "(Error|Exception|Traceback|CUDA|OOM)" | tail -5)
            
            send_telegram "🔴 DetZero Training CRASHED!

PID: $CURRENT_PID
Time: $(date '+%Y-%m-%d %H:%M:%S')
Checks: $CHECK_COUNT
GPU: $(get_gpu_status)

Last log lines:
$LAST_LINES

Log: $LATEST_LOG"
        else
            send_telegram "🔴 DetZero Training CRASHED!

PID: $CURRENT_PID
Time: $(date '+%Y-%m-%d %H:%M:%S')
Checks: $CHECK_COUNT
GPU: $(get_gpu_status)

No log file found"
        fi
        
        rm -f "$TRAINING_PID_FILE"
        exit 1
    fi
    
    # Periodic status update (every 30 checks = ~30 minutes)
    if [ $((CHECK_COUNT % 30)) -eq 0 ]; then
        GPU_STATUS=$(get_gpu_status)
        echo "[$(date '+%H:%M:%S')] Check #$CHECK_COUNT - Process alive (PID: $CURRENT_PID, GPU: $GPU_STATUS)"
    fi
done
