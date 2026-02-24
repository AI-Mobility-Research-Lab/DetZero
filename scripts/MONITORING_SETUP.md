# Training Monitoring Setup

## Prerequisites

OpenClaw configured (for WhatsApp/Telegram) OR email configured on your system.

## Quick Start (Log File Method - Easiest)

The monitor defaults to logging alerts to a file. No setup needed!

```bash
# Start monitoring (logs to /tmp/detzero_training_alert.log)
tmux new-session -d -s monitor
tmux send-keys -t monitor "cd ~/projects/DetZero && bash scripts/monitor_training.sh" C-m

# Check alerts
tail -f /tmp/detzero_training_alert.log
```

## Setup for WhatsApp (Recommended)

### 1. Link WhatsApp to OpenClaw

```bash
# Link your WhatsApp account
openclaw channels login --channel whatsapp

# This will show a QR code - scan it with WhatsApp on your phone
# (WhatsApp > Settings > Linked Devices > Link a Device)
```

### 2. Get Your Phone Number

Your phone number in E.164 format (e.g., `+1234567890`).

### 3. Test WhatsApp Messaging

```bash
openclaw message send \
    --channel whatsapp \
    --target "+1234567890" \
    --message "🧪 Test: DetZero training monitor"
```

### 4. Configure the Monitor

Edit `scripts/monitor_training.sh`:
```bash
NOTIFY_METHOD="whatsapp"
WHATSAPP_TARGET="+1234567890"  # Your phone number
```

## Setup for Telegram

### 1. Get Your Telegram Chat ID

```bash
# Start a chat with your OpenClaw bot on Telegram first
# Then list peers to find your chat ID
openclaw directory peers list --channel telegram
```

### 2. Configure the Monitor

Edit `scripts/monitor_training.sh`:
```bash
NOTIFY_METHOD="telegram"
TELEGRAM_TARGET="123456789"  # Your chat ID
```

## Setup for Email

### 1. Configure Email Settings

Edit `scripts/monitor_training.sh`:
```bash
NOTIFY_METHOD="email"
EMAIL_TO="your@email.com"
EMAIL_FROM="training@yourserver.com"
SMTP_HOST="smtp.gmail.com"  # Or your SMTP server
SMTP_PORT="587"
```

### 2. Ensure mail command is available

```bash
# Install mailutils if needed
sudo apt-get install mailutils
```

### 4. Start the Monitor

Run the monitor in a separate tmux session:
```bash
# Create new tmux session for monitor
tmux new-session -d -s monitor

# Start the monitor
tmux send-keys -t monitor "cd ~/projects/DetZero && bash scripts/monitor_training.sh" C-m

# Check monitor output
tmux attach -t monitor
# Press Ctrl+B then D to detach
```

Or run in background:
```bash
nohup bash scripts/monitor_training.sh > /tmp/training_monitor.log 2>&1 &
```

## Notification Methods Comparison

| Method | Setup Difficulty | Reliability | Real-time |
|--------|-----------------|-------------|-----------|
| Log File | ⭐ Easiest | ⭐⭐⭐ High | ❌ No (manual check) |
| WhatsApp | ⭐⭐ Easy | ⭐⭐⭐ High | ✅ Yes |
| Telegram | ⭐⭐⭐ Medium | ⭐⭐⭐ High | ✅ Yes |
| Email | ⭐⭐ Easy | ⭐⭐ Medium | ⚠️ Delayed |

**Recommendation:** Start with log file method, then upgrade to WhatsApp if you want real-time alerts.

## What the Monitor Does

- Checks training process every 60 seconds
- Sends Telegram alert if training crashes
- Includes crash details: PID, timestamp, GPU status, error logs
- Sends periodic status updates every 30 minutes
- Automatically stops when training completes or crashes

## Notifications You'll Receive

**Log File (default):**
```bash
# Check alerts
tail -f /tmp/detzero_training_alert.log

# Example output:
[2026-02-24 02:30:15] 🔴 DetZero Training CRASHED!
PID: 330704
Time: 2026-02-24 02:30:15
...
```

**WhatsApp/Telegram:**

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

**Log file method:**
- Check if monitor is running: `ps aux | grep monitor_training`
- View alerts: `cat /tmp/detzero_training_alert.log`
- Monitor logs: `tail -f /tmp/training_monitor.log`

**WhatsApp "not linked" error:**
- Run: `openclaw channels login --channel whatsapp`
- Scan QR code with WhatsApp app
- Verify: `openclaw channels list`

**Telegram "chat not found" error:**
- Make sure you've started a chat with the bot on Telegram
- Verify your chat ID is correct
- Try using numeric chat ID instead of @username

**Monitor not detecting crash:**
- Check if monitor process is still running: `ps aux | grep monitor_training`
- Check monitor logs: `tail -f /tmp/training_monitor.log`

**No notifications received:**
- Test OpenClaw: `openclaw status`
- Check channel status: `openclaw channels list`
- Verify bot has permission to send messages
