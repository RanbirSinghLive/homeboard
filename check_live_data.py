#!/usr/bin/env python3
"""
Check which trips in STM GTFS-Realtime feed have live delay data vs scheduled only
"""

import os
import yaml
import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

def load_config():
    """Load configuration from config.yaml or environment variables"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        pass
    
    # Override with environment variables if set
    if 'STM_API_KEY' in os.environ:
        if 'transit' not in config:
            config['transit'] = {}
        config['transit']['api_key'] = os.environ['STM_API_KEY']
    
    if 'STOP_IDS' in os.environ:
        if 'transit' not in config:
            config['transit'] = {}
        config['transit']['stop_ids'] = [s.strip() for s in os.environ['STOP_IDS'].split(',')]
    
    if 'transit' not in config:
        config['transit'] = {'stop_ids': []}
    
    return config

def check_live_data():
    config = load_config()
    api_key = config.get('transit', {}).get('api_key', '')
    stop_ids = config.get('transit', {}).get('stop_ids', [])
    
    if not api_key:
        print("Error: STM API key not found in config.yaml or STM_API_KEY environment variable")
        return
    
    if not stop_ids:
        print("Error: No stop IDs configured")
        return
    
    print(f"Checking live data for stops: {stop_ids}")
    print("=" * 80)
    
    headers = {
        'apikey': api_key,
        'Accept': 'application/x-protobuf'
    }
    
    STM_GTFS_REALTIME_URL = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
    
    try:
        response = requests.get(STM_GTFS_REALTIME_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        stop_ids_set = set(str(sid) for sid in stop_ids)
        now = datetime.now()
        
        live_trips = []
        scheduled_trips = []
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                route_id = trip_update.trip.route_id if trip_update.trip.HasField('route_id') else 'N/A'
                
                for stop_time_update in trip_update.stop_time_update:
                    stop_id = str(stop_time_update.stop_id)
                    
                    if stop_id in stop_ids_set:
                        arrival_time = None
                        has_delay = False
                        delay_seconds = None
                        
                        if stop_time_update.HasField('arrival'):
                            arrival_time = stop_time_update.arrival.time
                            if stop_time_update.arrival.HasField('delay'):
                                has_delay = True
                                delay_seconds = stop_time_update.arrival.delay
                        elif stop_time_update.HasField('departure'):
                            arrival_time = stop_time_update.departure.time
                            if stop_time_update.departure.HasField('delay'):
                                has_delay = True
                                delay_seconds = stop_time_update.departure.delay
                        
                        if arrival_time:
                            arrival_dt = datetime.fromtimestamp(arrival_time)
                            delta = arrival_dt - now
                            minutes_until = int(delta.total_seconds() / 60)
                            
                            if 0 <= minutes_until <= 60:
                                trip_info = {
                                    'route': route_id,
                                    'stop_id': stop_id,
                                    'minutes': minutes_until,
                                    'has_delay': has_delay,
                                    'delay_seconds': delay_seconds
                                }
                                
                                if has_delay:
                                    live_trips.append(trip_info)
                                else:
                                    scheduled_trips.append(trip_info)
        
        print(f"\nLIVE TRIPS (with delay data): {len(live_trips)}")
        print("-" * 80)
        if live_trips:
            for trip in sorted(live_trips, key=lambda x: x['minutes'])[:10]:
                delay_str = f"{trip['delay_seconds']}s" if trip['delay_seconds'] else "0s"
                status = "LATE" if trip['delay_seconds'] and trip['delay_seconds'] > 60 else "ON-TIME" if trip['delay_seconds'] and trip['delay_seconds'] >= -60 else "EARLY"
                print(f"Route {trip['route']:>3} | Stop {trip['stop_id']:>5} | {trip['minutes']:>2}m | Delay: {delay_str:>6} | {status}")
        else:
            print("  None found")
        
        print(f"\nSCHEDULED TRIPS (no delay data): {len(scheduled_trips)}")
        print("-" * 80)
        if scheduled_trips:
            for trip in sorted(scheduled_trips, key=lambda x: x['minutes'])[:10]:
                print(f"Route {trip['route']:>3} | Stop {trip['stop_id']:>5} | {trip['minutes']:>2}m | Scheduled time only")
        else:
            print("  None found")
        
        print(f"\nSUMMARY:")
        print(f"  Total trips: {len(live_trips) + len(scheduled_trips)}")
        print(f"  Live (with delay): {len(live_trips)} ({len(live_trips)/(len(live_trips)+len(scheduled_trips))*100:.1f}%)" if (live_trips + scheduled_trips) else "  Live (with delay): 0")
        print(f"  Scheduled only: {len(scheduled_trips)} ({len(scheduled_trips)/(len(live_trips)+len(scheduled_trips))*100:.1f}%)" if (live_trips + scheduled_trips) else "  Scheduled only: 0")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_live_data()

