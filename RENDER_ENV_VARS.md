# Render Environment Variables Setup

Since `config.yaml` is not deployed (it's in `.gitignore` for security), you need to set these environment variables in Render.

## Required Environment Variables

Go to your Render service → **Environment** tab → Add these variables:

### 1. STM API Key (Required for transit data)
```
STM_API_KEY=l7dfc00d148df14e208dccdc5d7d0e7bf6
```

### 2. Location (Required for weather/AQI)
```
LATITUDE=45.2840
LONGITUDE=-73.3328
```

### 3. Transit Stop IDs (Required for transit departures)
```
STOP_IDS=52886,52887
```

### 4. BIXI Station IDs (Required for BIXI data)
```
BIXI_STATION_IDS=486,889
```

## How to Add in Render

1. Go to your Render dashboard
2. Click on your `homeboard` service
3. Click the **"Environment"** tab
4. Click **"Add Environment Variable"**
5. Add each variable one by one:
   - Key: `STM_API_KEY`
   - Value: `l7dfc00d148df14e208dccdc5d7d0e7bf6`
   - Click "Save"
6. Repeat for all variables above
7. Render will automatically redeploy when you save

## Quick Copy-Paste

If you want to add them all at once, here's the format:

```
STM_API_KEY=l7dfc00d148df14e208dccdc5d7d0e7bf6
LATITUDE=45.2840
LONGITUDE=-73.3328
STOP_IDS=52886,52887
BIXI_STATION_IDS=486,889
```

## After Adding Variables

1. Render will automatically redeploy
2. Check the logs to make sure it starts successfully
3. Visit your Render URL to see the dashboard!

## Optional: Test the API

Once deployed, test the health endpoint:
```
https://your-app-name.onrender.com/api/health
```

You should see: `{"status":"healthy","timestamp":"..."}`

