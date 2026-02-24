# 🚀 Netlify CLI Deployment Instructions

You're logged in and ready to deploy! Follow these steps:

## Step 1: Navigate to Directory

```bash
cd web_visualizer
```

## Step 2: Deploy (Interactive)

Run this command:

```bash
netlify deploy --dir=. --prod
```

## Step 3: Answer the Prompts

### Prompt 1: "What would you like to do?"
**Select**: `+ Create & configure a new project`
- Use arrow keys to select
- Press Enter

### Prompt 2: "Team:"
**Select**: `AI & Mobility Research Lab`
- Press Enter

### Prompt 3: "Site name (optional):"
**Type**: `detzero-3d-viz` (or leave blank for random name)
- Press Enter

## Step 4: Wait for Deployment

You'll see:
```
Deploying to main site URL...
✔ Finished hashing 
✔ CDN requesting 5 files
✔ Finished uploading 5 files
✔ Deploy is live!
```

## Step 5: Get Your URL

You'll receive:
```
Website URL:       https://detzero-3d-viz.netlify.app
```

## Alternative: One-Line Deploy

If you want to skip prompts, use:

```bash
netlify deploy --dir=. --prod --site-name detzero-3d-viz --team "AI & Mobility Research Lab"
```

## What Gets Deployed

- ✅ index.html (9KB)
- ✅ app.js (12KB)
- ✅ netlify.toml (285B)
- ✅ data/detection_data.json (203KB)
- ✅ data/refined_data.json (440KB)
- ✅ data/summary.json (254B)

**Total**: ~650KB

## Expected Output

```
Deploy path:        /home/aimob/projects/DetZero/web_visualizer
Configuration path: /home/aimob/projects/DetZero/web_visualizer/netlify.toml
Deploying to main site URL...
✔ Finished hashing 5 files
✔ CDN requesting 5 files
✔ Finished uploading 5 files
✔ Deploy is live!

Logs:              https://app.netlify.com/sites/detzero-3d-viz/deploys/...
Website URL:       https://detzero-3d-viz.netlify.app
```

## Verification

After deployment, open the URL and check:

1. ✅ Page loads without errors
2. ✅ Both 3D views show boxes
3. ✅ Frame slider works (0-49)
4. ✅ Statistics update
5. ✅ Mouse controls work
6. ✅ Play button works

## Troubleshooting

### "Site name already taken"
- Choose a different name
- Or leave blank for auto-generated name

### "Deploy failed"
- Check internet connection
- Verify all files are present
- Try again

### "Authentication error"
- Run: `netlify logout`
- Then: `netlify login`
- Try deployment again

## Quick Commands Reference

```bash
# Check status
netlify status

# Deploy draft (preview)
netlify deploy --dir=.

# Deploy production
netlify deploy --dir=. --prod

# Open site in browser
netlify open:site

# View deployment logs
netlify logs

# List all sites
netlify sites:list
```

## After Deployment

### Share Your URL
```
https://detzero-3d-viz.netlify.app
```

### Update Deployment
To update after changes:
```bash
netlify deploy --dir=. --prod
```

### Custom Domain (Optional)
```bash
netlify domains:add yourdomain.com
```

## Need Help?

- Check: `netlify help`
- Docs: https://docs.netlify.com/cli/get-started/
- Status: `netlify status`

---

**Ready? Run the command and follow the prompts!** 🚀
