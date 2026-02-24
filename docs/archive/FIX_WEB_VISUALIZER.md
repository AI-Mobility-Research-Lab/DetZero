# 🔧 Fix Web Visualizer - Missing Data Files

## Problem

The web visualizer shows "Loading visualization data..." forever because the JSON data files don't exist yet.

## Root Cause

The `web_visualizer/data/` directory and JSON files were never created. The `prepare_data.py` script needs to be run to convert the pickle files to JSON.

---

## ✅ SOLUTION: Generate the Data Files

### Step 1: Open a NEW Terminal

**IMPORTANT:** You need a fresh terminal that's NOT stuck in the Netlify CLI prompt.

1. Open a new terminal window/tab
2. Navigate to the project directory:
   ```bash
   cd /home/aimob/projects/DetZero
   ```

### Step 2: Run the Data Preparation Script

```bash
python3 web_visualizer/prepare_data.py \
    --detection detection/output/baseline_vehicle_test.pkl \
    --refined data/waymo_custom/refining/result/Vehicle_final_frame.pkl \
    --output_dir web_visualizer/data \
    --max_frames 50
```

### Step 3: Verify Files Were Created

```bash
ls -lh web_visualizer/data/
```

You should see:
```
detection_data.json  (200-300KB)
refined_data.json    (400-500KB)
summary.json         (few KB)
```

### Step 4: Redeploy to Netlify

Now that the data files exist, redeploy using Netlify Drop:

1. Go to: https://app.netlify.com/drop
2. Drag the `web_visualizer` folder
3. Wait 30 seconds
4. Open the new URL

---

## Alternative: Use the Shell Script

I created a helper script:

```bash
# Make it executable
chmod +x generate_web_data.sh

# Run it
./generate_web_data.sh
```

---

## What This Does

The script will:
1. Load the detection results (Vehicle.pkl)
2. Load the refined results (Vehicle_final_frame.pkl)
3. Convert first 50 frames to JSON format
4. Create 3 files:
   - `detection_data.json` - Before refinement
   - `refined_data.json` - After refinement
   - `summary.json` - Statistics

---

## Expected Output

```
Loading detection data...
Loading refined data...
Converting data (max 50 frames)...
Saving detection data to web_visualizer/data/detection_data.json...
Saving refined data to web_visualizer/data/refined_data.json...

============================================================
Data preparation complete!
============================================================

Files created:
  - web_visualizer/data/detection_data.json
  - web_visualizer/data/refined_data.json
  - web_visualizer/data/summary.json

Summary:
  Total frames: 50
  Detection boxes: 560
  Refined boxes: 1246
  Detection avg score: 0.823
  Refined avg score: 0.799

Next steps:
  1. Deploy the web_visualizer folder to Netlify
  2. Open the deployed URL in your browser
============================================================
```

---

## Troubleshooting

### Issue: "No such file or directory: Vehicle.pkl"

**Check if files exist:**
```bash
ls -lh data/waymo_custom/detection/result/
ls -lh data/waymo_custom/refining/result/
```

**If files are missing:** Run the DetZero pipeline first

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Install dependencies:**
```bash
pip install numpy
```

### Issue: Still stuck in Netlify CLI

**Kill the process:**
```bash
# Find the process
ps aux | grep netlify

# Kill it (replace PID with actual number)
kill -9 <PID>

# Or kill all netlify processes
pkill -9 netlify
```

---

## Quick Commands Summary

```bash
# 1. Generate data (in NEW terminal)
python3 web_visualizer/prepare_data.py \
    --detection detection/output/baseline_vehicle_test.pkl \
    --refined data/waymo_custom/refining/result/Vehicle_final_frame.pkl \
    --output_dir web_visualizer/data \
    --max_frames 50

# 2. Verify
ls -lh web_visualizer/data/

# 3. Deploy
# Go to https://app.netlify.com/drop
# Drag web_visualizer folder
```

---

## After Fixing

Once the data files are created and you redeploy:

1. ✅ Page will load immediately
2. ✅ Both 3D views will show boxes
3. ✅ Frame slider will work (0-49)
4. ✅ Statistics will show correct numbers
5. ✅ Play button will work

---

## Why This Happened

The data files were supposed to be generated before deployment, but the Netlify CLI got stuck in interactive mode, preventing the data preparation script from running.

---

**Next Action:** Open a new terminal and run the python command above! 🚀
