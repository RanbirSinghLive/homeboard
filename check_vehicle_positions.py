#!/usr/bin/env python3
"""
Check STM Vehicle Positions feed to see if it contains delay information
"""

import os
import yaml
import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = {}
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        pass
    
    if 'STM_API_KEY' in os.environ:
        if 'transit' not in config:
            config['transit'] = {}
        config['transit']['api_key'] = os.environ['STM_API_KEY']
    
    return config

def check_vehicle_positions():
    config = load_config()
    api_key = config.get('transit', {}).get('api_key', '')
    
    if not api_key:
        print("Error: STM API key not found")
        return
    
    print("Checking STM Vehicle Positions Feed")
    print("=" * 80)
    
    headers = {
        'apikey': api_key,
        'Accept': 'application/x-protobuf'
    }
    
    url = 'https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        print(f"✓ Feed downloaded: {len(response.content)} bytes")
        print(f"✓ Entities: {len(feed.entity)}")
        print()
        
        # Sample a few vehicles to see what data is available
        sample_count = 0
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                sample_count += 1
                
                if sample_count <= 5:  # Show first 5 as examples
                    print(f"Vehicle {sample_count}:")
                    if vehicle.HasField('trip'):
                        trip = vehicle.trip
                        print(f"  Route ID: {trip.route_id if trip.HasField('route_id') else 'N/A'}")
                        print(f"  Trip ID: {trip.trip_id if trip.HasField('trip_id') else 'N/A'}")
                        print(f"  Direction: {trip.direction_id if trip.HasField('direction_id') else 'N/A'}")
                    
                    if vehicle.HasField('position'):
                        pos = vehicle.position
                        print(f"  Position: Lat {pos.latitude:.4f}, Lon {pos.longitude:.4f}")
                    
                    if vehicle.HasField('current_stop_sequence'):
                        print(f"  Current Stop Sequence: {vehicle.current_stop_sequence}")
                    
                    if vehicle.HasField('current_status'):
                        status_map = {
                            0: 'INCOMING_AT',
                            1: 'STOPPED_AT',
                            2: 'IN_TRANSIT_TO'
                        }
                        print(f"  Status: {status_map.get(vehicle.current_status, 'UNKNOWN')}")
                    
                    if vehicle.HasField('timestamp'):
                        ts = datetime.fromtimestamp(vehicle.timestamp)
                        print(f"  Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if vehicle.HasField('congestion_level'):
                        print(f"  Congestion Level: {vehicle.congestion_level}")
                    
                    if vehicle.HasField('occupancy_status'):
                        print(f"  Occupancy Status: {vehicle.occupancy_status}")
                    
                    print()
        
        print("=" * 80)
        print("ANALYSIS:")
        print("  Vehicle Positions feed contains:")
        print("    - Current GPS location of buses")
        print("    - Current stop sequence")
        print("    - Vehicle status (incoming, stopped, in transit)")
        print("    - Timestamp of last update")
        print()
        print("  However, this feed does NOT contain:")
        print("    - Delay information")
        print("    - Predicted arrival times at stops")
        print()
        print("  To calculate delays, you would need to:")
        print("    1. Match vehicle positions to trips")
        print("    2. Compare current position to scheduled position")
        print("    3. Calculate delay based on distance/time")
        print("    (This is complex and may not be accurate)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_vehicle_positions()

