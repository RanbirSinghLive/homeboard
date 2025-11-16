# GitHub Pages Setup Guide

This guide explains how to host the Departure Board frontend on GitHub Pages.

## Important Note

GitHub Pages only serves static files (HTML, CSS, JavaScript). The Flask backend (`app.py`) cannot run on GitHub Pages. You have two options:

1. **Run the backend locally** - The frontend will work when you access it from the same machine running the backend
2. **Host the backend elsewhere** - Deploy the backend to a service like Heroku, Railway, Render, or Fly.io, then point the frontend to that URL

## Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - **Source**: GitHub Actions
4. Save the settings

### 2. Deploy the Frontend

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will automatically deploy the frontend when you push to the `main` branch.

To trigger a deployment:
```bash
git push origin main
```

The workflow will:
- Copy only the static files (index.html and related assets)
- Deploy them to GitHub Pages
- Your site will be available at: `https://YOUR_USERNAME.github.io/homeboard/`

### 3. Configure Backend URL

Since the backend won't be on GitHub Pages, you need to tell the frontend where to find it.

#### Option A: URL Parameter (Recommended for Testing)

Add the backend URL as a query parameter:
```
https://YOUR_USERNAME.github.io/homeboard/?api=https://your-backend.herokuapp.com
```

#### Option B: Modify index.html (For Permanent Setup)

Edit `index.html` and change the API_BASE line:
```javascript
const API_BASE = 'https://your-backend.herokuapp.com';
```

Then commit and push - the GitHub Actions workflow will redeploy.

## Backend Hosting Options

### Option 1: Heroku (Free Tier Available)

1. Install Heroku CLI
2. Create a `Procfile`:
   ```
   web: python app.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 2: Railway

1. Connect your GitHub repo to Railway
2. Railway will auto-detect Python and install dependencies
3. Set environment variables for your API keys
4. Deploy automatically on push

### Option 3: Render

1. Create a new Web Service on Render
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variables

### Option 4: Fly.io

1. Install Fly CLI
2. Run `fly launch`
3. Deploy with `fly deploy`

## Environment Variables

When hosting the backend, you'll need to set these environment variables or use a config file:

- `STM_API_KEY` - Your STM API key
- Location and stop IDs can be set in `config.yaml` or as environment variables

## Testing

1. Deploy the frontend to GitHub Pages
2. Deploy the backend to your chosen service
3. Access the frontend with the backend URL parameter:
   ```
   https://YOUR_USERNAME.github.io/homeboard/?api=https://your-backend-url.com
   ```

## Troubleshooting

### CORS Errors

If you see CORS errors, make sure your backend has CORS enabled (already configured in `app.py` with `flask_cors`).

### API Not Found

- Check that your backend URL is correct
- Verify the backend is running and accessible
- Check browser console for error messages

### Mixed Content Warnings

If your GitHub Pages site is HTTPS but your backend is HTTP, browsers will block the requests. Use HTTPS for your backend.

## Local Development

For local development, the frontend will automatically use `window.location.origin`, which works when accessing `http://localhost:5001` directly.

