# Quick Start Guide - Running on Localhost

## Step-by-Step Instructions

### 1. Install Python Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

If you get permission errors, use:
```bash
pip install --user -r requirements.txt
```

### 2. (Optional) Configure Your Settings

Edit `config.yaml` to add your:
- STM stop IDs
- BIXI station IDs  
- Location coordinates

If you skip this, the app will use default Montreal coordinates and show empty transit/BIXI data.

### 3. Start the Server

Run the Flask backend:

```bash
python app.py
```

You should see output like:
```
INFO:__main__:Starting Home Departure Board API server
INFO:__main__:Configuration: {...}
 * Running on http://0.0.0.0:5000
```

### 4. Open the Dashboard

Open your web browser and go to:

```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

The dashboard should load automatically!

### 5. Stop the Server

Press `Ctrl+C` in the terminal to stop the server.

## Troubleshooting

### Port 5000 Already in Use

If you get an error that port 5000 is in use:

**Option 1:** Find and stop the process using port 5000:
```bash
# On Mac/Linux:
lsof -ti:5000 | xargs kill -9

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Option 2:** Change the port in `app.py` (last line):
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed to 5001
```

### Module Not Found Errors

Make sure all dependencies are installed:
```bash
pip install Flask flask-cors requests PyYAML
```

### No Data Showing

- Check that your `config.yaml` has valid stop IDs and station IDs
- Check the browser console (F12) for errors
- Check the terminal where Flask is running for error messages
- Weather and AQI should work even without configuration (uses default Montreal location)

## Testing the API

You can test individual endpoints:

- Health check: http://localhost:5000/api/health
- Dashboard data: http://localhost:5000/api/dashboard
- Weather: http://localhost:5000/api/weather
- BIXI: http://localhost:5000/api/bixi

## Next Steps

- Configure your transit stops and BIXI stations in `config.yaml`
- Set your home location for accurate weather/AQI
- Adjust walking time and buffer time for the leave-now indicator

