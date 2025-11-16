# Simple One-Service Deployment (Easiest Option!)

Since your Flask app already serves `index.html`, you can host **everything on one service** - no need to split frontend/backend!

## Option 1: Render (Recommended - Easiest)

**Why Render?**
- ✅ Completely free tier
- ✅ Zero configuration needed
- ✅ Auto-deploys from GitHub
- ✅ HTTPS included
- ✅ Can host your entire Flask app (frontend + backend together)

### Steps:

1. **Go to [render.com](https://render.com)** and sign up with GitHub

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your `homeboard` GitHub repository
   - Render will auto-detect it's a Python app!

3. **Configure (usually auto-detected):**
   - **Name**: `homeboard` (or whatever you want)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. **Add Environment Variables:**
   - Click "Environment" tab
   - Add: `STM_API_KEY` = your STM API key
   - Optional: `LATITUDE=45.2840`, `LONGITUDE=-73.3328`, etc.

5. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes for first deploy
   - Done! Your app is live at: `https://homeboard.onrender.com`

**That's it!** Your entire app (frontend + backend) is now live on one URL.

### Render Free Tier:
- ✅ **Free forever** (no credit card needed)
- ✅ 750 hours/month (enough for 24/7)
- ⚠️ Spins down after 15 min inactivity (first request may take 10-30 seconds)
- ✅ 512 MB RAM
- ✅ Perfect for this app!

---

## Option 2: PythonAnywhere (Also Simple)

**Why PythonAnywhere?**
- ✅ Free tier available
- ✅ Made specifically for Python apps
- ✅ Simple web interface

### Steps:

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Upload your code:**
   - Go to "Files" tab
   - Upload your files (or clone from GitHub)

3. **Create a Web App:**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose Flask, Python 3.10
   - Point it to your `app.py`

4. **Set environment variables:**
   - In "Web" tab → "Environment variables"
   - Add your STM_API_KEY, etc.

5. **Reload:**
   - Click the green "Reload" button
   - Done!

**Free tier:** Limited to 1 web app, 512 MB storage, 100 seconds CPU/day

---

## Option 3: Replit (Easiest for Testing)

**Why Replit?**
- ✅ Super easy - just click "Run"
- ✅ Free tier
- ✅ Can import from GitHub

### Steps:

1. **Go to [replit.com](https://replit.com)** and sign up

2. **Import from GitHub:**
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Enter: `RanbirSinghLive/homeboard`

3. **Add secrets (environment variables):**
   - Click the lock icon (Secrets)
   - Add: `STM_API_KEY`, etc.

4. **Run:**
   - Click "Run" button
   - Replit will give you a URL like: `https://homeboard.ranbirsingh.repl.co`

**Free tier:** Always-on option available, but may sleep after inactivity

---

## Recommendation: Use Render!

Render is the best balance of:
- ✅ Ease of setup (almost zero config)
- ✅ Free tier (generous)
- ✅ Reliability
- ✅ Auto-deployment from GitHub

Your app will be live at: `https://your-app-name.onrender.com`

**No need for GitHub Pages + separate backend!** Everything runs together. 🎉

