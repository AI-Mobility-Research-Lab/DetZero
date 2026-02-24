#!/bin/bash
# Monitor training process and send alert if it crashes

# Configuration
TRAINING_PID_FILE="/tmp/detzero_training.pid"
CHECK_INTERVAL=60  # Check every 60 seconds
ALERT_LOG="/tmp/detzero_training_alert.log"

# Notification method: "whatsapp", "telegram", "email", or "log"
NOTIFY_METHOD="log"

# WhatsApp configuration (if using WhatsApp)
WHATSAPP_TARGET=""  # Your phone number in E.164 format (e.g., "+1234567890")

# Telegram configuration (if using Telegram)
TELEGRAM_TARGET=""  # Your Telegram chat ID (e.g., "123456789")

# Email configuration (if using email)
EMAIL_TO=""  # Your email address
EMAIL_FROM="${EMAIL_FROM:-training-monitor@localhost}"
SMTP_HOST="${SMTP_HOST:-localhost}"
SMTP_PORT="${SMTP_PORT:-25}"

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

# Send notification based on configured method
send_notification() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$NOTIFY_METHOD" in
        whatsapp)
            if [ -z "$WHATSAPP_TARGET" ]; then
                echo "✗ WhatsApp target not configured"
                return 1
            fi
            openclaw message send \
                --channel whatsapp \
                --target "$WHATSAPP_TARGET" \
                --message "$message" \
                2>&1 | grep -q "success" && echo "✓ WhatsApp notification sent" || echo "✗ Failed to send WhatsApp"
            ;;
        telegram)
            if [ -z "$TELEGRAM_TARGET" ]; then
                echo "✗ Telegram target not configured"
                return 1
            fi
            openclaw message send \
                --channel telegram \
                --target "$TELEGRAM_TARGET" \
                --message "$message" \
                2>&1 | grep -q "success" && echo "✓ Telegram notification sent" || echo "✗ Failed to send Telegram"
            ;;
        email)
            if [ -z "$EMAIL_TO" ]; then
                echo "✗ Email recipient not configured"
                return 1
            fi
            echo "$message" | mail -s "DetZero Training Alert" "$EMAIL_TO" \
                && echo "✓ Email notification sent" || echo "✗ Failed to send email"
            ;;
        log)
            echo "[$timestamp] $message" >> "$ALERT_LOG"
            echo "✓ Alert logged to $ALERT_LOG"
            ;;
        *)
            echo "✗ Unknown notification method: $NOTIFY_METHOD"
            return 1
            ;;
    esac
}

# Get GPU status
get_gpu_status() {
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A"
}

# Main monitoring loop
echo "=========================================="
echo "DetZero Training Monitor"
echo "=========================================="
echo "Notification method: $NOTIFY_METHOD"
case "$NOTIFY_METHOD" in
    whatsapp) echo "WhatsApp target: $WHATSAPP_TARGET" ;;
    telegram) echo "Telegram target: $TELEGRAM_TARGET" ;;
    email) echo "Email to: $EMAIL_TO" ;;
    log) echo "Alert log: $ALERT_LOG" ;;
esac
echo "Check interval: ${CHECK_INTERVAL}s"
echo "=========================================="

# Find initial PID
CURRENT_PID=$(get_training_pid)

if [ -z "$CURRENT_PID" ]; then
    echo "✗ No training process found!"
    send_notification "⚠️ DetZero Training Monitor: No training process found at startup"
    exit 1
fi

echo "✓ Found training process: PID $CURRENT_PID"
echo "$CURRENT_PID" > "$TRAINING_PID_FILE"

# Send startup notification
GPU_STATUS=$(get_gpu_status)
send_notification "🚀 DetZero Training Monitor Started

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
            
            send_notification "🔴 DetZero Training CRASHED!

PID: $CURRENT_PID
Time: $(date '+%Y-%m-%d %H:%M:%S')
Checks: $CHECK_COUNT
GPU: $(get_gpu_status)

Last log lines:
$LAST_LINES

Log: $LATEST_LOG"
        else
            send_notification "🔴 DetZero Training CRASHED!

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
