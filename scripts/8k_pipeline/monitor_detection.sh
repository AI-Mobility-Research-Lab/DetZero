#!/bin/bash
# Monitor detection progress

echo "=========================================="
echo "DetZero 8K Detection Monitor"
echo "=========================================="
echo ""

# Check if PID file exists
if [ ! -f logs/detection_8k.pid ]; then
    echo "❌ No detection process found (logs/detection_8k.pid missing)"
    echo ""
    echo "Start detection with:"
    echo "  ./scripts/8k_pipeline/run_detection_8k_background.sh"
    exit 1
fi

PID=$(cat logs/detection_8k.pid)

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Detection is running (PID: $PID)"
    echo ""
    
    # Show process info
    echo "Process Info:"
    ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
    echo ""
    
    # Show recent log entries
    echo "=========================================="
    echo "Recent Log Entries (last 20 lines):"
    echo "=========================================="
    if [ -f logs/detection_8k.log ]; then
        tail -20 logs/detection_8k.log
    else
        echo "Log file not found yet..."
    fi
    echo ""
    
    # Show output file size
    if [ -f output_8k/detection/val_detections.pkl ]; then
        SIZE=$(du -h output_8k/detection/val_detections.pkl | cut -f1)
        echo "Output file size: $SIZE"
    fi
    echo ""
    
    echo "=========================================="
    echo "Monitor Commands:"
    echo "=========================================="
    echo "  Watch logs:     tail -f logs/detection_8k.log"
    echo "  Watch output:   tail -f logs/detection_8k_nohup.out"
    echo "  Check process:  ps -p $PID"
    echo "  Stop process:   kill $PID"
    echo ""
else
    echo "❌ Detection process not running (PID: $PID)"
    echo ""
    
    # Check if completed
    if [ -f output_8k/detection/val_detections.pkl ]; then
        echo "✅ Detection appears to be complete!"
        echo ""
        echo "Results:"
        ls -lh output_8k/detection/val_detections.pkl
        echo ""
        echo "Validate results:"
        echo "  python3 -c \"import pickle; d=pickle.load(open('output_8k/detection/val_detections.pkl','rb')); print(f'Frames: {len(d)}'); print(f'Avg boxes: {sum(len(r[\\\"score\\\"]) for r in d)/len(d):.2f}')\""
    else
        echo "Check logs for errors:"
        echo "  tail -50 logs/detection_8k.log"
        echo "  tail -50 logs/detection_8k_nohup.out"
    fi
    echo ""
fi
