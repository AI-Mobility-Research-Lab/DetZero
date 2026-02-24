# Training Monitoring Setup

## Prerequisites

You have OpenClaw configured with Telegram bot access.

## Setup Steps

### 1. Get Your Telegram Chat ID

First, start a conversation with your OpenClaw bot on Telegram:
1. Open Telegram and find your OpenClaw bot
2. Send any message to the bot (e.g., "hello")

Then get your chat ID:
```bash
# List all Telegram peers/contacts
openclaw directory peers list --channel telegram

# Or check recent messages to find your chat ID
openclaw message list --channel telegram --limit 5
```

Your chat ID will be a number like `123456789` or `-100123456789` (for groups).

### 2. Configure the Monitor Script

Edit `scripts/monitor_training.sh` and set your chat ID:
```bash
TELEGRAM_TARGET="123456789"  # Replace with your actual chat ID
```

### 3. Test the Notification

Test that OpenClaw can send you a message:
```bash
openclaw message send \
    --channel telegram \
    --target "123456789" \
    --message "🧪 Test: DetZero training monitor is ready"
```

You should receive a message on Telegram. If not, check:
- Bot is started in your Telegram chat
- Chat ID is correct
- OpenClaw is properly configured (`openclaw status`)

### 4. Start the Monitor

Run the monitor in a separate tmux session:
```bash
# Create new tmux session for monitor
tmux new-session -d -s monitor

# Start the monitor
tmux send-keys -t monitor "cd /home/aimob/projects/DetZero && bash scripts/monitor_training.sh" C-m

# Check monitor output
tmux attach -t monitor
# Press Ctrl+B then D to detach
```

Or run in background:
```bash
nohup bash scripts/monitor_training.sh > /tmp/training_monitor.log 2>&1 &
```

## What the Monitor Does

- Checks training process every 60 seconds
- Sends Telegram alert if training crashes
- Includes crash details: PID, timestamp, GPU status, error logs
- Sends periodic status updates every 30 minutes
- Automatically stops when training completes or crashes

## Notifications You'll Receive

**Startup:**
```
🚀 DetZero Training Monitor Started
PID: 330704
GPU: 96, 6488, 8188, 77
Checking every 60s
```

**Crash Alert:**
```
🔴 DetZero Training CRASHED!
PID: 330704
Time: 2026-02-24 02:30:15
Checks: 145
GPU: 0, 156, 8188, 45

Last log lines:
[error details]

Log: detection/output/.../log_train_20260223-213035.txt
```

## Stopping the Monitor

If running in tmux:
```bash
tmux kill-session -t monitor
```

If running in background:
```bash
pkill -f "monitor_training.sh"
```

## Troubleshooting

**"chat not found" error:**
- Make sure you've started a chat with the bot on Telegram
- Verify your chat ID is correct
- Try using numeric chat ID instead of @username

**Monitor not detecting crash:**
- Check if monitor process is still running: `ps aux | grep monitor_training`
- Check monitor logs: `tail -f /tmp/training_monitor.log`

**No notifications received:**
- Test OpenClaw: `openclaw status`
- Check bot token: `openclaw config get telegram.botToken`
- Verify bot has permission to send messages
