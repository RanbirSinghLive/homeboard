# Render Troubleshooting Guide

## Common Issues and Solutions

### 1. "config.yaml not found" Warning

**This is NORMAL and expected!** 
- `config.yaml` is in `.gitignore` (for security)
- The app automatically uses environment variables instead
- Make sure you've added all environment variables in Render

### 2. App Not Loading / Blank Page

**Check:**
1. Visit your Render URL: `https://your-app.onrender.com`
2. Check browser console (F12 → Console tab) for errors
3. Check Render logs for errors

**Common causes:**
- Missing environment variables
- GTFS data still downloading (first startup takes 1-2 minutes)
- App crashed - check logs

### 3. API Calls Failing

**Symptoms:** Dashboard shows "Loading..." or errors

**Solutions:**
1. **Check environment variables are set:**
   - Go to Render → Your Service → Environment tab
   - Verify: `STM_API_KEY`, `LATITUDE`, `LONGITUDE`, `STOP_IDS`, `BIXI_STATION_IDS`

2. **Test the API directly:**
   ```
   https://your-app.onrender.com/api/health
   ```
   Should return: `{"status":"healthy","timestamp":"..."}`

3. **Check CORS:** Already enabled in app.py, but verify if you see CORS errors

### 4. First Request is Slow

**Normal behavior on Render free tier:**
- App spins down after 15 min of inactivity
- First request after spin-down takes 10-30 seconds
- Subsequent requests are fast

**Solution:** Keep the app "warm" by visiting it regularly, or upgrade to paid tier

### 5. GTFS Download Taking Long Time

**First startup:**
- App downloads ~50MB GTFS data on first run
- This can take 1-2 minutes
- Subsequent starts use cached data (if available)

**Check logs:** You should see "Downloading GTFS static data..." then "Loaded X trip headsigns..."

### 6. Environment Variables Not Working

**Verify format:**
- No spaces around `=`
- Comma-separated lists: `STOP_IDS=52886,52887` (no spaces after commas)
- Numbers: `LATITUDE=45.2840` (use decimal point, not comma)

**After adding variables:**
- Render auto-redeploys
- Wait for deployment to complete
- Check logs to verify variables are loaded

### 7. Check Render Logs

1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for:
   - ✅ "Server starting on http://0.0.0.0:XXXX"
   - ✅ "Configuration loaded" or "using environment variables"
   - ❌ Any ERROR messages

### 8. Test Endpoints

Test these URLs in your browser:

```
https://your-app.onrender.com/api/health
https://your-app.onrender.com/api/weather
https://your-app.onrender.com/api/dashboard
```

If these work but the main page doesn't, it's a frontend issue.

### 9. Clear Browser Cache

Sometimes old cached files cause issues:
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or clear browser cache

### 10. Check Network Tab

1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Reload page
4. Look for failed requests (red)
5. Check what error they show

## Quick Health Check

Run these commands to test your deployed app:

```bash
# Test health endpoint
curl https://your-app.onrender.com/api/health

# Test dashboard endpoint
curl https://your-app.onrender.com/api/dashboard

# Test weather endpoint
curl https://your-app.onrender.com/api/weather
```

If these return JSON, your backend is working!

## Still Having Issues?

1. **Check Render logs** - Most errors show up there
2. **Check browser console** - Frontend errors show there
3. **Verify environment variables** - Make sure all are set correctly
4. **Wait for first startup** - GTFS download takes time on first run

