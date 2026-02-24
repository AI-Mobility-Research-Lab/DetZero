# DetZero 3D Web Visualizer

Interactive web-based 3D visualization for comparing detection results before and after refinement.

## Features

- 🎨 Side-by-side comparison of detection vs refined results
- 🎮 Interactive 3D navigation (rotate, pan, zoom)
- 📊 Real-time statistics display
- ▶️ Frame-by-frame playback
- 🎯 Color-coded confidence levels
- 📱 Responsive design
- 🚀 Zero dependencies (uses CDN)

## Quick Start

### 1. Prepare Data

Run the data preparation script from the DetZero root directory:

```bash
python web_visualizer/prepare_data.py \
    --detection detection/output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug/eval/epoch_30/val/result.pkl \
    --refined data/waymo_custom/refining/result/Vehicle_final_frame.pkl \
    --max_frames 50
```

This will create JSON files in `web_visualizer/data/`:
- `detection_data.json` - Detection results
- `refined_data.json` - Refined results
- `summary.json` - Statistics summary

### 2. Deploy to Netlify

#### Option A: Netlify CLI (Recommended)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to web_visualizer directory
cd web_visualizer

# Deploy
netlify deploy --dir=. --prod
```

#### Option B: Netlify Drop

1. Go to https://app.netlify.com/drop
2. Drag and drop the `web_visualizer` folder
3. Get your deployment URL

#### Option C: Git Integration

1. Push `web_visualizer` to a GitHub repository
2. Connect to Netlify via GitHub
3. Set build directory to `web_visualizer`
4. Deploy

### 3. View

Open the deployed URL in your browser. You should see:
- Left panel: Before refinement (detection only)
- Right panel: After refinement (GRM+PRM+CRM)

## Controls

### Mouse Controls
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out

### UI Controls
- **Frame Slider**: Navigate to specific frame
- **Play Button**: Auto-play through frames
- **Previous/Next**: Step through frames
- **Reset View**: Return camera to default position

## Color Legend

- 🟢 **Green**: High confidence (>0.9)
- 🟡 **Yellow**: Medium confidence (0.7-0.9)
- 🔴 **Red**: Low confidence (<0.7)

## File Structure

```
web_visualizer/
├── index.html          # Main HTML file
├── app.js             # Three.js visualization logic
├── netlify.toml       # Netlify configuration
├── prepare_data.py    # Data conversion script
├── README.md          # This file
└── data/              # Generated data files
    ├── detection_data.json
    ├── refined_data.json
    └── summary.json
```

## Customization

### Adjust Number of Frames

To export more or fewer frames:

```bash
python web_visualizer/prepare_data.py \
    --detection <path> \
    --refined <path> \
    --max_frames 100  # Change this number
```

### Modify Colors

Edit `app.js` in the `addBox` function:

```javascript
// Change color thresholds or colors
if (score > 0.9) {
    color = 0x00ff00; // Green
} else if (score > 0.7) {
    color = 0xffff00; // Yellow
} else {
    color = 0xff0000; // Red
}
```

### Change Camera Position

Edit `app.js` in the `setupScenes` function:

```javascript
this.cameraBefore.position.set(50, 50, 50); // Change x, y, z
```

## Troubleshooting

### Data Not Loading

1. Check browser console for errors (F12)
2. Ensure JSON files are in `data/` directory
3. Verify JSON files are valid (use jsonlint.com)

### Slow Performance

1. Reduce number of frames with `--max_frames`
2. Close other browser tabs
3. Use a modern browser (Chrome, Firefox, Edge)

### Boxes Not Visible

1. Click "Reset View" button
2. Try zooming out (scroll wheel)
3. Check if data files contain boxes

## Technical Details

### Dependencies (CDN)
- Three.js v0.160.0
- OrbitControls

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Data Format

JSON structure for each frame:

```json
{
  "frame_id": 0,
  "sequence_name": "k_6001_8000_camera_v",
  "boxes": [
    {
      "center": [x, y, z],
      "size": [length, width, height],
      "rotation": heading_angle,
      "score": confidence_score,
      "class": "Vehicle"
    }
  ]
}
```

## Performance Tips

- Limit frames to 50-100 for smooth performance
- Use Chrome for best WebGL performance
- Close unnecessary browser tabs
- Ensure good GPU drivers

## License

Part of the DetZero project. See main repository for license details.

## Support

For issues or questions:
1. Check browser console for errors
2. Verify data files are correctly generated
3. Ensure modern browser with WebGL support
4. Check Netlify deployment logs

## Credits

- DetZero: https://arxiv.org/abs/2306.06023
- Three.js: https://threejs.org/
- Netlify: https://www.netlify.com/
