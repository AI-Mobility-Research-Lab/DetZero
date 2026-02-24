#!/bin/bash
# Quick status check

echo "DetZero 8K Pipeline Status"
echo "=========================================="
echo ""

# Check detection
if [ -f logs/detection_8k.pid ]; then
    PID=$(cat logs/detection_8k.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🟢 Detection: RUNNING (PID: $PID)"
    else
        echo "🔴 Detection: STOPPED"
    fi
else
    echo "⚪ Detection: NOT STARTED"
fi

# Check output files
echo ""
echo "Output Files:"
if [ -f output_8k/detection/val_detections.pkl ]; then
    SIZE=$(du -h output_8k/detection/val_detections.pkl | cut -f1)
    echo "  ✅ Detection results: $SIZE"
else
    echo "  ⏳ Detection results: Not yet"
fi

if [ -f output_8k/tracking/tracking_val.pkl ]; then
    SIZE=$(du -h output_8k/tracking/tracking_val.pkl | cut -f1)
    echo "  ✅ Tracking results: $SIZE"
else
    echo "  ⏳ Tracking results: Not yet"
fi

# Check logs
echo ""
echo "Recent Activity:"
if [ -f logs/detection_8k.log ]; then
    echo "  Last log entry:"
    tail -1 logs/detection_8k.log | sed 's/^/    /'
fi

echo ""
echo "Commands:"
echo "  Monitor:  ./scripts/8k_pipeline/monitor_detection.sh"
echo "  Logs:     tail -f logs/detection_8k.log"
echo ""
