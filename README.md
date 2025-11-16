# Home Departure Board

A wall-mounted or tablet-displayed web dashboard that shows everything needed to leave the house in under 5 seconds of glance time.

## Features

- **Real-time Transit Departures** - STM bus and metro departures
- **BIXI Station Status** - Bike and dock availability
- **Weather Overview** - Temperature, conditions, wind, precipitation
- **Air Quality (AQI)** - Current air quality index
- **Sunrise/Sunset Times** - Daily sunrise and sunset
- **Leave-Now Indicator** - Dynamic indicator based on walking time and next departure
- **Alerts** - STM service disruptions and weather warnings

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment and install Python dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the application:**
   Edit `config.yaml` with your settings:
   - Add your STM stop IDs
   - Add your BIXI station IDs
   - Set your location (latitude/longitude)
   - Adjust walking time and buffer time

4. **Start the backend server:**
   
   **Option A: Use the startup script (recommended):**
   ```bash
   ./start.sh
   ```
   
   **Option B: Manual start:**
   ```bash
   source venv/bin/activate  # Activate virtual environment
   python3 app.py
   ```
   
   The server will start on `http://localhost:5001` (port 5001 to avoid AirPlay conflicts on macOS)

5. **Open the dashboard:**
   Open your browser and go to: `http://localhost:5001`

## Configuration

Edit `config.yaml` to customize:

### Transit Stops
Find your STM stop IDs:
- Visit [STM website](https://www.stm.info/en/info/networks/metro/bus)
- Use the STM mobile app
- Look for stop codes at bus stops

### BIXI Stations
Find BIXI station IDs:
- Use the BIXI mobile app
- Visit [BIXI website](https://bixi.com)
- Station IDs are displayed on station screens

### Location
Set your home location for weather and AQI:
- Use Google Maps to find your latitude/longitude
- Default is set to downtown Montreal (45.5017, -73.5673)

### Walking Time & Buffer
- `walking_time`: Minutes to walk to your transit stop
- `buffer_time`: Extra buffer time before departure

## Running on Hardware

### Raspberry Pi

1. Install Python and dependencies on your Pi
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. Open the dashboard in a browser (Chromium in kiosk mode recommended)
4. Set up auto-start (see below)

### Android Tablet / Amazon Fire HD

1. Install a web server app (e.g., "Simple HTTP Server")
2. Upload `index.html` to the server
3. Point the server to your backend API (update API_BASE in index.html if needed)
4. Open the dashboard in a browser
5. Set browser to fullscreen/kiosk mode

### Auto-Start on Raspberry Pi

Create a systemd service file `/etc/systemd/system/homeboard.service`:

```ini
[Unit]
Description=Home Departure Board
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/path/to/homeboard
ExecStart=/usr/bin/python3 /path/to/homeboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable homeboard
sudo systemctl start homeboard
```

## API Endpoints

The backend provides the following endpoints:

- `GET /api/dashboard` - Get all dashboard data (recommended)
- `GET /api/transit` - Get transit departures
- `GET /api/bixi` - Get BIXI station status
- `GET /api/weather` - Get weather data
- `GET /api/aqi` - Get air quality data
- `GET /api/sunrise-sunset` - Get sunrise/sunset times
- `GET /api/alerts` - Get alerts
- `GET /api/leave-now` - Get leave-now indicator
- `GET /api/health` - Health check

## Troubleshooting

### Backend not starting
- Check Python version: `python3 --version` (should be 3.8+)
- Make sure virtual environment is activated: `source venv/bin/activate`
- Verify dependencies: `pip list` (should show Flask, flask-cors, requests, PyYAML)
- Check port 5001 is not in use: `lsof -i :5001`
- If you see "ModuleNotFoundError", run: `pip install -r requirements.txt` inside the virtual environment

### No transit data
- Verify stop IDs in `config.yaml` are correct
- Check STM API is accessible: `curl https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates`
- Note: Full GTFS-Realtime parsing requires additional setup (see below)

### No BIXI data
- Verify station IDs in `config.yaml` are correct
- Check BIXI API: `curl https://api-core.bixi.com/gbfs/en/station_status.json`

### Weather/AQI not loading
- Verify location coordinates in `config.yaml`
- Check internet connection
- Verify Open-Meteo API is accessible

## Advanced: Full STM GTFS-Realtime Support

The current implementation includes a simplified STM data structure. For full GTFS-Realtime parsing, you'll need to:

1. Install protobuf and GTFS-Realtime bindings:
   ```bash
   pip install protobuf gtfs-realtime-bindings
   ```

2. Update `fetch_stm_departures()` in `app.py` to parse the protobuf feed

## Development

### Project Structure

```
homeboard/
├── app.py              # Flask backend API
├── index.html          # Front-end dashboard
├── config.yaml         # Configuration file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Widgets

1. Add data fetching function in `app.py`
2. Add API endpoint in `app.py`
3. Add rendering function in `index.html`
4. Add widget HTML in dashboard render function

## License

This project is provided as-is for personal use.

## Credits

Built for Montréal commuters who need to leave the house quickly!

