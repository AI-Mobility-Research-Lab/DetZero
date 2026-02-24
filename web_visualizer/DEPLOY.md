# Deployment Guide for DetZero 3D Visualizer

## Quick Deploy to Netlify (Zero-Cost Preview)

### Method 1: Netlify Drop (Easiest - No Account Required)

1. **Prepare the folder**
   ```bash
   cd web_visualizer
   ```

2. **Create a ZIP file** (if needed)
   ```bash
   zip -r detzero-visualizer.zip . -x "*.pyc" -x "__pycache__/*" -x "*.py"
   ```

3. **Deploy**
   - Go to https://app.netlify.com/drop
   - Drag and drop the `web_visualizer` folder (or ZIP file)
   - Wait for deployment (usually <30 seconds)
   - Get your URL: `https://random-name.netlify.app`

### Method 2: Netlify CLI (More Control)

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy**
   ```bash
   cd web_visualizer
   netlify deploy --dir=. --prod
   ```

3. **Follow prompts**
   - Choose "Create & configure a new site"
   - Select your team (or create one)
   - Choose a site name (or use auto-generated)
   - Confirm deployment

4. **Get URL**
   - URL will be displayed: `https://your-site-name.netlify.app`

### Method 3: GitHub + Netlify (Continuous Deployment)

1. **Create GitHub repository**
   ```bash
   cd web_visualizer
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/detzero-viz.git
   git push -u origin main
   ```

2. **Connect to Netlify**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub
   - Select your repository
   - Build settings:
     - Build command: (leave empty)
     - Publish directory: `.`
   - Click "Deploy site"

3. **Get URL**
   - URL: `https://your-site-name.netlify.app`

## Verification

After deployment, verify:

1. ✅ Page loads without errors
2. ✅ Both 3D views are visible
3. ✅ Boxes appear in both panels
4. ✅ Frame slider works
5. ✅ Statistics update when changing frames
6. ✅ Mouse controls work (rotate, pan, zoom)

## Troubleshooting

### "Failed to fetch data"
- Check browser console (F12)
- Ensure `data/` folder was included in deployment
- Verify JSON files are valid

### Blank 3D views
- Check browser console for WebGL errors
- Try different browser (Chrome recommended)
- Ensure GPU acceleration is enabled

### Slow loading
- Reduce `--max_frames` when preparing data
- Check network tab in browser dev tools
- Ensure good internet connection

## Sharing

Once deployed, share the URL with anyone:
- No login required
- Works on mobile devices
- No installation needed
- Free hosting on Netlify

## Example URLs

After deployment, your URL will look like:
- `https://detzero-viz-abc123.netlify.app`
- `https://your-custom-name.netlify.app`

## Cost

- ✅ **100% FREE** for preview deployments
- ✅ No credit card required
- ✅ Unlimited bandwidth for personal projects
- ✅ HTTPS included
- ✅ Global CDN

## Next Steps

1. Deploy using one of the methods above
2. Open the URL in your browser
3. Share with your team
4. Explore the 3D visualization!

## Support

If you encounter issues:
1. Check Netlify deployment logs
2. Verify all files are present
3. Test locally first (use `python -m http.server 8000`)
4. Check browser console for errors
