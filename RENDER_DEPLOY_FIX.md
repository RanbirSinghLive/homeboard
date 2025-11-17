# Render Not Getting Latest Changes - Fix Guide

## Quick Fix: Manual Redeploy

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Sign in to your account

2. **Find Your Service:**
   - Click on your "homeboard" service (or whatever you named it)

3. **Manual Deploy:**
   - Click the **"Manual Deploy"** button (top right)
   - Select **"Deploy latest commit"**
   - Wait for deployment to complete (2-3 minutes)

## Check Auto-Deploy Settings

1. **Go to your service settings:**
   - Click your service → **Settings** tab

2. **Verify Auto-Deploy:**
   - Under "Build & Deploy"
   - Make sure **"Auto-Deploy"** is set to **"Yes"**
   - Branch should be set to **"main"**

3. **If Auto-Deploy is off:**
   - Turn it on
   - Save changes
   - Render will automatically deploy the latest commit

## Verify Latest Commit is Deployed

1. **Check Render Logs:**
   - Go to your service → **Logs** tab
   - Look for the latest commit hash
   - Should match: `fbeba2b` (Add styled route badges)

2. **Check Build Logs:**
   - Go to your service → **Events** tab
   - Look for the most recent deployment
   - Check if it shows the latest commit

## Force a New Deployment

If manual deploy doesn't work:

1. **Make a small change and push:**
   ```bash
   # Add a comment or whitespace change
   git commit --allow-empty -m "Trigger Render deployment"
   git push origin main
   ```

2. **Or trigger via Render API:**
   - Go to Render → Your Service → Settings
   - Look for "Manual Deploy" button
   - Click it to force a new deployment

## Check if Branch is Correct

1. **Verify your local branch:**
   ```bash
   git branch
   # Should show: * main
   ```

2. **Verify remote branch:**
   ```bash
   git branch -r
   # Should show: origin/main
   ```

3. **In Render settings:**
   - Make sure "Branch" is set to **"main"** (not "master" or something else)

## Common Issues

### Issue: Render is deploying old code
**Solution:** Clear Render's build cache
- Go to Settings → Advanced
- Click "Clear build cache"
- Then manually deploy

### Issue: Changes not showing in browser
**Solution:** Clear browser cache
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or clear browser cache completely

### Issue: Auto-deploy not working
**Solution:** 
- Check that your GitHub repo is properly connected
- Verify webhook is set up (Render should do this automatically)
- Try disconnecting and reconnecting the GitHub repo

## Verify Deployment

After deploying, check:

1. **Visit your app:**
   ```
   https://homeboard.onrender.com
   ```

2. **Check for new features:**
   - Light mode should be active
   - Route badges should be styled (blue for 57/71, purple border for 107)
   - Should see max 10 departures (2 per route+direction)

3. **Check browser console:**
   - Press F12 → Console tab
   - Look for any errors

## Still Not Working?

1. **Check Render status page:**
   - https://status.render.com
   - See if there are any ongoing issues

2. **Check Render logs for errors:**
   - Go to Logs tab
   - Look for ERROR or WARNING messages
   - Share these if you need help

3. **Verify GitHub connection:**
   - In Render → Settings
   - Check that GitHub repo is connected
   - Try disconnecting and reconnecting if needed

