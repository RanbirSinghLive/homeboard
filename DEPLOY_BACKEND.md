# Deploy Backend to Railway (Free)

This guide will help you deploy your Flask backend to Railway for free.

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account (easiest option)
3. Verify your email if prompted

## Step 2: Create New Project

1. Click **"New Project"** in Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Select your `homeboard` repository
4. Railway will automatically detect it's a Python project

## Step 3: Configure Environment Variables

In your Railway project, go to **Variables** tab and add:

### Required Variables:

```
STM_API_KEY=your_stm_api_key_here
```

### Optional Variables (if not using config.yaml):

```
LATITUDE=45.2840
LONGITUDE=-73.3328
STOP_IDS=52886,52887
BIXI_STATION_IDS=486,889
```

**To get your STM API key:**
1. Visit: https://portail.developpeurs.stm.info/apihub
2. Register/login
3. Go to "Authentication & Credentials"
4. Create an API key
5. Copy and paste it into Railway

## Step 4: Deploy

1. Railway will automatically start deploying when you connect the repo
2. Wait for the build to complete (usually 2-3 minutes)
3. Once deployed, Railway will give you a URL like: `https://your-app-name.up.railway.app`

## Step 5: Update Frontend

Once you have your Railway URL, update `index.html`:

```javascript
const DEFAULT_API_BASE = 'https://your-app-name.up.railway.app';
```

Or use the URL parameter:
```
https://ranbirsinghlive.github.io/homeboard/?api=https://your-app-name.up.railway.app
```

## Step 6: Test

1. Visit your Railway URL: `https://your-app-name.up.railway.app/api/health`
2. You should see: `{"status":"healthy","timestamp":"..."}`
3. Visit your GitHub Pages site with the API parameter
4. The dashboard should load data!

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is in the root directory
- Check Railway logs for error messages

### API Returns Errors
- Verify environment variables are set correctly
- Check Railway logs: Click on your service → "View Logs"
- Make sure STM_API_KEY is set if you want transit data

### CORS Errors
- The backend already has CORS enabled, but if you see errors, check that your Railway URL is correct

## Railway Free Tier Limits

- **$5 free credit per month** (usually enough for a small app)
- **512 MB RAM**
- **1 GB storage**
- **100 GB bandwidth**

For a small API like this, the free tier should be plenty!

## Alternative: Render (Also Free)

If Railway doesn't work, you can use Render:

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create a new **Web Service**
4. Connect your repository
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
6. Add environment variables (same as Railway)
7. Deploy!

Render free tier:
- **750 hours/month** (enough for 24/7)
- **512 MB RAM**
- **Spins down after 15 min inactivity** (first request may be slow)

