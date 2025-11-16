"""
Home Departure Board - Flask Backend API
Fetches and aggregates data from STM, BIXI, Weather, and AQI sources.
"""

import os
import yaml
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GTFS-Realtime availability check
GTFS_AVAILABLE = False
try:
    from google.transit import gtfs_realtime_pb2
    GTFS_AVAILABLE = True
except ImportError:
    logger.warning("GTFS-Realtime bindings not available. Install with: pip install gtfs-realtime-bindings")

app = Flask(__name__)
CORS(app)

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except FileNotFoundError:
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return {
            'transit': {'stop_ids': []},
            'bixi': {'station_ids': []},
            'location': {'lat': 45.5017, 'lon': -73.5673},  # Montreal default
            'walking_time': 5,
            'buffer_time': 2,
            'refresh_interval': 30
        }

CONFIG = load_config()

# API endpoints
STM_GTFS_REALTIME_URL = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
# BIXI GBFS API - using velobixi.com endpoint (working as of 2024)
BIXI_GBFS_URL = "https://gbfs.velobixi.com/gbfs/en/station_status.json"
BIXI_STATION_INFO_URL = "https://gbfs.velobixi.com/gbfs/en/station_information.json"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_stm_departures(stop_ids: List[str]) -> List[Dict]:
    """
    Fetch real-time STM departures for given stop IDs.
    Returns list of departure objects.
    """
    try:
        api_key = CONFIG.get('transit', {}).get('api_key', '')
        
        if not api_key:
            logger.warning("STM API key not configured. Get one from https://portail.developpeurs.stm.info/apihub")
            return []
        
        if not GTFS_AVAILABLE:
            logger.error("GTFS-Realtime bindings not available. Install with: pip install gtfs-realtime-bindings")
            return []
        
        logger.info(f"Fetching STM departures for stops: {stop_ids}")
        
        # STM API requires API key in headers
        headers = {
            'apikey': api_key,
            'Accept': 'application/x-protobuf'
        }
        
        response = requests.get(STM_GTFS_REALTIME_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        logger.info(f"STM API response received: {len(response.content)} bytes")
        
        # Parse GTFS-Realtime protobuf feed
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        now = datetime.now()
        departures = []
        # Convert stop_ids to set for fast lookup (handle both string and int)
        stop_ids_set = set(str(sid) for sid in stop_ids)
        
        # Process each entity in the feed
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                
                # Check each stop time update
                for stop_time_update in trip_update.stop_time_update:
                    stop_id = str(stop_time_update.stop_id)
                    
                    # Filter by requested stop IDs
                    if stop_id in stop_ids_set:
                        # Get arrival or departure time
                        arrival_time = None
                        if stop_time_update.HasField('arrival'):
                            arrival_time = stop_time_update.arrival.time
                        elif stop_time_update.HasField('departure'):
                            arrival_time = stop_time_update.departure.time
                        
                        if arrival_time:
                            # Convert Unix timestamp to datetime
                            arrival_dt = datetime.fromtimestamp(arrival_time)
                            
                            # Calculate minutes until arrival
                            delta = arrival_dt - now
                            minutes_until = int(delta.total_seconds() / 60)
                            
                            # Only include future departures (within next 60 minutes)
                            if 0 <= minutes_until <= 60:
                                # Get route info from trip descriptor
                                route_id = trip_update.trip.route_id if trip_update.trip.HasField('route_id') else 'N/A'
                                
                                # Get trip ID for reference
                                trip_id = trip_update.trip.trip_id if trip_update.trip.HasField('trip_id') else ''
                                
                                # Try to get stop name from stop_time_update if available
                                stop_name = f'Stop {stop_id}'
                                if stop_time_update.HasField('stop_id'):
                                    # Could enhance with GTFS static data lookup
                                    pass
                                
                                departures.append({
                                    'route_number': route_id,
                                    'headsign': f'Route {route_id}',  # Simplified - would need GTFS static data for actual headsign
                                    'stop_code': stop_id,
                                    'stop_name': stop_name,
                                    'arrival_minutes': minutes_until,
                                    'arrival_time': arrival_dt.strftime('%H:%M'),
                                    'scheduled_time': arrival_dt.isoformat(),
                                    'trip_id': trip_id
                                })
        
        # Sort by arrival time
        departures.sort(key=lambda x: x['arrival_minutes'])
        
        # Limit to next 10 departures per stop
        departures = departures[:20]
        
        logger.info(f"Found {len(departures)} departures for stops {stop_ids}")
        return departures
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.error("STM API: Invalid API key. Check your API key in config.yaml")
        elif e.response.status_code == 401:
            logger.error("STM API: Unauthorized. Check your API key in config.yaml")
        else:
            logger.error(f"STM API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"Error fetching STM departures: {e}", exc_info=True)
        return []


def fetch_bixi_status(station_ids: List[str]) -> List[Dict]:
    """
    Fetch BIXI station status for given station IDs.
    Returns list of station status objects.
    """
    try:
        logger.info(f"Fetching BIXI status for stations: {station_ids}")
        
        # Fetch station status
        status_response = requests.get(BIXI_GBFS_URL, timeout=10)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Fetch station information
        info_response = requests.get(BIXI_STATION_INFO_URL, timeout=10)
        info_response.raise_for_status()
        info_data = info_response.json()
        
        # Create mapping of station_id to station info
        # Handle both string and int station IDs
        station_info_map = {}
        for station in info_data.get('data', {}).get('stations', []):
            sid = station.get('station_id')
            station_info_map[sid] = station
            station_info_map[str(sid)] = station  # Also index by string for lookup
        
        # Filter and combine data
        # Convert station_ids from config (strings) to match API format (may be int or string)
        station_ids_normalized = [str(sid) for sid in station_ids]
        
        stations = []
        for station_status in status_data.get('data', {}).get('stations', []):
            station_id = str(station_status.get('station_id', ''))
            if station_id in station_ids_normalized:
                # Try both int and string lookup for station info
                sid_int = station_status.get('station_id')
                station_info = station_info_map.get(sid_int) or station_info_map.get(station_id) or {}
                stations.append({
                    'station_id': station_id,
                    'name': station_info.get('name', f'Station {station_id}'),
                    'bikes_available': station_status.get('num_bikes_available', 0),
                    'docks_available': station_status.get('num_docks_available', 0),
                    'is_renting': station_status.get('is_renting', False),
                    'is_returning': station_status.get('is_returning', False)
                })
        
        logger.info(f"Found {len(stations)} BIXI stations out of {len(station_ids)} requested")
        if len(stations) == 0 and len(station_ids) > 0:
            logger.warning(f"No matching stations found. Requested IDs: {station_ids}")
            logger.info(f"Available station IDs (first 10): {[str(s.get('station_id')) for s in status_data.get('data', {}).get('stations', [])[:10]]}")
        return stations
    except Exception as e:
        logger.error(f"Error fetching BIXI status: {e}")
        return []


def fetch_weather(lat: float, lon: float) -> Dict:
    """
    Fetch weather data from Open-Meteo API.
    Returns weather object with current conditions.
    """
    try:
        logger.info(f"Fetching weather for location: {lat}, {lon}")
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation_probability',
            'timezone': 'America/Montreal',
            'forecast_days': 1
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current', {})
        
        # Map weather codes to conditions
        weather_code = current.get('weather_code', 0)
        condition_map = {
            0: 'Clear', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
            45: 'Foggy', 48: 'Depositing Rime Fog',
            51: 'Light Drizzle', 53: 'Moderate Drizzle', 55: 'Dense Drizzle',
            56: 'Light Freezing Drizzle', 57: 'Dense Freezing Drizzle',
            61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
            66: 'Light Freezing Rain', 67: 'Heavy Freezing Rain',
            71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
            77: 'Snow Grains', 80: 'Slight Rain Showers', 81: 'Moderate Rain Showers',
            82: 'Violent Rain Showers', 85: 'Slight Snow Showers', 86: 'Heavy Snow Showers',
            95: 'Thunderstorm', 96: 'Thunderstorm with Hail', 99: 'Thunderstorm with Heavy Hail'
        }
        
        weather = {
            'temperature': current.get('temperature_2m', 0),
            'feels_like': current.get('apparent_temperature', 0),
            'condition': condition_map.get(weather_code, 'Unknown'),
            'weather_code': weather_code,
            'wind_speed': current.get('wind_speed_10m', 0),
            'wind_direction': current.get('wind_direction_10m', 0),
            'precipitation_probability': current.get('precipitation_probability', 0),
            'humidity': current.get('relative_humidity_2m', 0),
            'units': {
                'temperature': data.get('current_units', {}).get('temperature_2m', '°C'),
                'wind_speed': data.get('current_units', {}).get('wind_speed_10m', 'km/h')
            }
        }
        
        logger.info(f"Weather fetched: {weather['temperature']}°C, {weather['condition']}")
        return weather
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return {}


def fetch_aqi(lat: float, lon: float) -> Dict:
    """
    Fetch air quality data from Open-Meteo API.
    Returns AQI object.
    """
    try:
        logger.info(f"Fetching AQI for location: {lat}, {lon}")
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'air_quality',
            'timezone': 'America/Montreal'
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current', {})
        aqi_value = current.get('air_quality', {}).get('european_aqi', 0)
        
        # Categorize AQI
        if aqi_value <= 50:
            category = 'Good'
            severity = 'info'
        elif aqi_value <= 100:
            category = 'Moderate'
            severity = 'info'
        elif aqi_value <= 150:
            category = 'Unhealthy for Sensitive Groups'
            severity = 'warning'
        elif aqi_value <= 200:
            category = 'Unhealthy'
            severity = 'warning'
        elif aqi_value <= 300:
            category = 'Very Unhealthy'
            severity = 'critical'
        else:
            category = 'Hazardous'
            severity = 'critical'
        
        aqi = {
            'value': int(aqi_value),
            'category': category,
            'severity': severity,
            'pm2_5': current.get('air_quality', {}).get('pm2_5', 0),
            'pm10': current.get('air_quality', {}).get('pm10', 0)
        }
        
        logger.info(f"AQI fetched: {aqi_value} ({category})")
        return aqi
    except Exception as e:
        logger.error(f"Error fetching AQI: {e}")
        return {'value': 0, 'category': 'Unknown', 'severity': 'info'}


def calculate_sunrise_sunset(lat: float, lon: float) -> Dict:
    """
    Calculate sunrise and sunset times for today.
    Returns dict with sunrise and sunset times.
    """
    try:
        logger.info(f"Calculating sunrise/sunset for location: {lat}, {lon}")
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'sunrise,sunset',
            'timezone': 'America/Montreal'
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get('daily', {})
        sunrise_times = daily.get('sunrise', [])
        sunset_times = daily.get('sunset', [])
        
        if sunrise_times and sunset_times:
            sunrise = sunrise_times[0]
            sunset = sunset_times[0]
            
            # Parse ISO format and extract time
            sunrise_dt = datetime.fromisoformat(sunrise.replace('Z', '+00:00'))
            sunset_dt = datetime.fromisoformat(sunset.replace('Z', '+00:00'))
            
            result = {
                'sunrise': sunrise_dt.strftime('%H:%M'),
                'sunset': sunset_dt.strftime('%H:%M'),
                'sunrise_iso': sunrise,
                'sunset_iso': sunset
            }
            
            logger.info(f"Sunrise: {result['sunrise']}, Sunset: {result['sunset']}")
            return result
    except Exception as e:
        logger.error(f"Error calculating sunrise/sunset: {e}")
    
    return {'sunrise': 'N/A', 'sunset': 'N/A'}


def fetch_alerts() -> List[Dict]:
    """
    Fetch alerts from STM and weather sources.
    Returns list of alert objects.
    """
    alerts = []
    
    # STM alerts (would need STM alerts API)
    # For now, return empty or mock structure
    logger.info("Fetching alerts (STM alerts API not implemented)")
    
    # Weather alerts could come from Environment Canada
    # For now, return empty list
    
    return alerts


def calculate_leave_now(departures: List[Dict], walking_time: int, buffer_time: int) -> Dict:
    """
    Calculate leave-now indicator based on soonest departure.
    Returns dict with leave status and message.
    """
    try:
        if not departures:
            return {
                'status': 'no_departures',
                'message': 'No departures available',
                'leave_in_minutes': None
            }
        
        # Find soonest departure (simplified - assumes departures have 'arrival_minutes' field)
        soonest = min(departures, key=lambda d: d.get('arrival_minutes', 999))
        arrival_minutes = soonest.get('arrival_minutes', 0)
        
        total_time_needed = walking_time + buffer_time
        leave_in = arrival_minutes - total_time_needed
        
        if leave_in <= 0:
            return {
                'status': 'leave_now',
                'message': 'Leave now!',
                'leave_in_minutes': 0,
                'departure_in_minutes': arrival_minutes
            }
        else:
            return {
                'status': 'leave_soon',
                'message': f'Leave in {leave_in} minutes',
                'leave_in_minutes': leave_in,
                'departure_in_minutes': arrival_minutes
            }
    except Exception as e:
        logger.error(f"Error calculating leave-now: {e}")
        return {
            'status': 'error',
            'message': 'Unable to calculate',
            'leave_in_minutes': None
        }


@app.route('/api/transit', methods=['GET'])
def get_transit():
    """Get STM transit departures"""
    logger.info("GET /api/transit")
    stop_ids = CONFIG.get('transit', {}).get('stop_ids', [])
    departures = fetch_stm_departures(stop_ids)
    return jsonify({'departures': departures})


@app.route('/api/bixi', methods=['GET'])
def get_bixi():
    """Get BIXI station status"""
    logger.info("GET /api/bixi")
    station_ids = CONFIG.get('bixi', {}).get('station_ids', [])
    stations = fetch_bixi_status(station_ids)
    return jsonify({'stations': stations})


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data"""
    logger.info("GET /api/weather")
    location = CONFIG.get('location', {})
    lat = location.get('lat', 45.5017)
    lon = location.get('lon', -73.5673)
    weather = fetch_weather(lat, lon)
    return jsonify(weather)


@app.route('/api/aqi', methods=['GET'])
def get_aqi():
    """Get air quality data"""
    logger.info("GET /api/aqi")
    location = CONFIG.get('location', {})
    lat = location.get('lat', 45.5017)
    lon = location.get('lon', -73.5673)
    aqi = fetch_aqi(lat, lon)
    return jsonify(aqi)


@app.route('/api/sunrise-sunset', methods=['GET'])
def get_sunrise_sunset():
    """Get sunrise and sunset times"""
    logger.info("GET /api/sunrise-sunset")
    location = CONFIG.get('location', {})
    lat = location.get('lat', 45.5017)
    lon = location.get('lon', -73.5673)
    times = calculate_sunrise_sunset(lat, lon)
    return jsonify(times)


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts"""
    logger.info("GET /api/alerts")
    alerts = fetch_alerts()
    return jsonify({'alerts': alerts})


@app.route('/api/leave-now', methods=['GET'])
def get_leave_now():
    """Get leave-now indicator"""
    logger.info("GET /api/leave-now")
    stop_ids = CONFIG.get('transit', {}).get('stop_ids', [])
    departures = fetch_stm_departures(stop_ids)
    walking_time = CONFIG.get('walking_time', 5)
    buffer_time = CONFIG.get('buffer_time', 2)
    leave_now = calculate_leave_now(departures, walking_time, buffer_time)
    return jsonify(leave_now)


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get all dashboard data in one request"""
    logger.info("GET /api/dashboard - Aggregating all data")
    
    location = CONFIG.get('location', {})
    lat = location.get('lat', 45.5017)
    lon = location.get('lon', -73.5673)
    stop_ids = CONFIG.get('transit', {}).get('stop_ids', [])
    station_ids = CONFIG.get('bixi', {}).get('station_ids', [])
    walking_time = CONFIG.get('walking_time', 5)
    buffer_time = CONFIG.get('buffer_time', 2)
    
    # Fetch all data
    departures = fetch_stm_departures(stop_ids)
    bixi_stations = fetch_bixi_status(station_ids)
    weather = fetch_weather(lat, lon)
    aqi = fetch_aqi(lat, lon)
    sunrise_sunset = calculate_sunrise_sunset(lat, lon)
    alerts = fetch_alerts()
    leave_now = calculate_leave_now(departures, walking_time, buffer_time)
    
    dashboard_data = {
        'transit': {'departures': departures},
        'bixi': {'stations': bixi_stations},
        'weather': weather,
        'aqi': aqi,
        'sunrise_sunset': sunrise_sunset,
        'alerts': alerts,
        'leave_now': leave_now,
        'last_updated': datetime.now().isoformat()
    }
    
    logger.info("Dashboard data aggregated successfully")
    return jsonify(dashboard_data)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/')
def index():
    """Serve the main dashboard page"""
    logger.info("Serving index.html")
    return send_from_directory(os.path.dirname(__file__), 'index.html')


if __name__ == '__main__':
    logger.info("Starting Home Departure Board API server")
    logger.info(f"Configuration: {CONFIG}")
    # Use port 5001 to avoid conflict with AirPlay on macOS
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Server starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

