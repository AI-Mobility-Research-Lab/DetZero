#!/bin/bash
# Quick training status check

echo "=== Training Status Check ==="
echo ""

# Check tmux sessions
echo "1. Tmux Sessions:"
tmux ls 2>/dev/null || echo "   No tmux sessions"
echo ""

# Check training process
echo "2. Training Process:"
TRAIN_PID=$(ps aux | grep "python tools/train.py" | grep -v grep | head -1 | awk '{print $2}')
if [ -z "$TRAIN_PID" ]; then
    echo "   ❌ No training process found"
else
    echo "   ✅ Training running (PID: $TRAIN_PID)"
    ps -o pid,tty,etime,cmd -p $TRAIN_PID | tail -1
fi
echo ""

# Check GPU usage
echo "3. GPU Status:"
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits | \
    awk -F', ' '{printf "   GPU Util: %s%%, Memory: %s/%s MiB (%.1f%%), Temp: %s°C, Power: %sW\n", $1, $2, $3, ($2/$3)*100, $4, $5}'
echo ""

# Check latest log
echo "4. Latest Training Log:"
LATEST_LOG=$(find detection/output -name "log_train*.txt" -type f 2>/dev/null | xargs ls -t | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "   Log: $LATEST_LOG"
    echo "   Last 3 lines:"
    tail -3 "$LATEST_LOG" | sed 's/^/   /'
else
    echo "   No training log found"
fi
echo ""

# Check if in tmux
if [ -n "$TRAIN_PID" ]; then
    TRAIN_TTY=$(ps -o tty -p $TRAIN_PID | tail -1 | tr -d ' ')
    if [[ $TRAIN_TTY == pts/* ]]; then
        # Check if this pts is owned by tmux
        TMUX_CHECK=$(pstree -s $TRAIN_PID | grep -o tmux)
        if [ -n "$TMUX_CHECK" ]; then
            echo "5. Persistence: ✅ Running in tmux (SSH-safe)"
        else
            echo "5. Persistence: ⚠️  Running in regular terminal (NOT SSH-safe)"
        fi
    else
        echo "5. Persistence: ✅ Running in background"
    fi
else
    echo "5. Persistence: N/A (no training process)"
fi

echo ""
echo "==========================="
