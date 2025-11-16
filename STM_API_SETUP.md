# STM API Setup Guide

## Step 1: Get Your API Key

1. **Visit the STM Developer Portal:**
   - Go to: https://portail.developpeurs.stm.info/apihub
   - Log in or create an account

2. **Navigate to Authentication & Credentials:**
   - In the portal, find the "Authentication & Credentials" section
   - Click on it to view your API keys

3. **Create a New API Key:**
   - Click "Create API Key" or "New API Key"
   - Give it a name (e.g., "Home Departure Board")
   - Copy the API key immediately (you may not be able to see it again)

## Step 2: Add API Key to Config

1. **Open `config.yaml`** in your project

2. **Find the `transit` section** and add your API key:
   ```yaml
   transit:
     api_key: "YOUR_API_KEY_HERE"  # Paste your API key between the quotes
     stop_ids:
       - "52886"
       - "52887"
   ```

3. **Save the file**

## Step 3: Test the API

1. **Restart your server:**
   ```bash
   # Stop the current server (Ctrl+C)
   ./start.sh
   ```

2. **Test the STM endpoint:**
   ```bash
   curl http://localhost:5001/api/transit
   ```

3. **Check the dashboard:**
   - Open http://localhost:5001
   - The transit departures section should show data (once parsing is implemented)

## Step 4: Full GTFS-Realtime Parsing (Optional)

The current implementation has simplified parsing. For full real-time departure data:

1. **Install protobuf libraries:**
   ```bash
   source venv/bin/activate
   pip install protobuf gtfs-realtime-bindings
   ```

2. **Update `fetch_stm_departures()` in `app.py`** to parse the protobuf feed

## Troubleshooting

### "Invalid API Key" Error
- Double-check that you copied the entire API key
- Make sure there are no extra spaces in `config.yaml`
- Verify the API key is active in the STM portal

### "Unauthorized" Error
- Your API key may have expired
- Check the STM portal to see if the key is still active
- Create a new API key if needed

### No Data Showing
- The current implementation uses simplified parsing
- Full parsing requires the protobuf libraries mentioned above
- Check server logs for error messages

## API Documentation

For more information about the STM API:
- Portal: https://portail.developpeurs.stm.info/apihub
- API: Open Data iBUS - GTFS-Realtime (v2.0)

