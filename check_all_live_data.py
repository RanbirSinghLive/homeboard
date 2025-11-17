#!/usr/bin/env python3
"""
Check if ANY trips in STM GTFS-Realtime feed have live delay data
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

def check_all_live_data():
    config = load_config()
    api_key = config.get('transit', {}).get('api_key', '')
    
    if not api_key:
        print("Error: STM API key not found")
        return
    
    print("Checking entire STM GTFS-Realtime feed for live delay data...")
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
        
        now = datetime.now()
        
        live_trips = []
        scheduled_trips = []
        route_stats = {}
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                route_id = trip_update.trip.route_id if trip_update.trip.HasField('route_id') else 'N/A'
                
                for stop_time_update in trip_update.stop_time_update:
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
                            if route_id not in route_stats:
                                route_stats[route_id] = {'live': 0, 'scheduled': 0}
                            
                            if has_delay:
                                live_trips.append({
                                    'route': route_id,
                                    'stop_id': str(stop_time_update.stop_id),
                                    'minutes': minutes_until,
                                    'delay_seconds': delay_seconds
                                })
                                route_stats[route_id]['live'] += 1
                            else:
                                scheduled_trips.append({
                                    'route': route_id,
                                    'stop_id': str(stop_time_update.stop_id),
                                    'minutes': minutes_until
                                })
                                route_stats[route_id]['scheduled'] += 1
        
        print(f"\nLIVE TRIPS (with delay data): {len(live_trips)}")
        print("-" * 80)
        if live_trips:
            # Show first 20 live trips
            for trip in sorted(live_trips, key=lambda x: x['minutes'])[:20]:
                delay_str = f"{trip['delay_seconds']}s" if trip['delay_seconds'] else "0s"
                status = "LATE" if trip['delay_seconds'] and trip['delay_seconds'] > 60 else "ON-TIME" if trip['delay_seconds'] and trip['delay_seconds'] >= -60 else "EARLY"
                print(f"Route {trip['route']:>3} | Stop {trip['stop_id']:>5} | {trip['minutes']:>2}m | Delay: {delay_str:>6} | {status}")
        else:
            print("  ⚠️  NO LIVE TRIPS FOUND - All trips are scheduled only")
        
        print(f"\nSCHEDULED TRIPS (no delay data): {len(scheduled_trips)}")
        print("-" * 80)
        print(f"  Total: {len(scheduled_trips)} trips")
        
        print(f"\nROUTE STATISTICS (first 20 routes):")
        print("-" * 80)
        sorted_routes = sorted(route_stats.items(), key=lambda x: x[1]['live'] + x[1]['scheduled'], reverse=True)
        for route_id, stats in sorted_routes[:20]:
            total = stats['live'] + stats['scheduled']
            live_pct = (stats['live'] / total * 100) if total > 0 else 0
            print(f"Route {route_id:>3}: {stats['live']:>3} live, {stats['scheduled']:>3} scheduled ({live_pct:>5.1f}% live)")
        
        print(f"\nSUMMARY:")
        print(f"  Total trips in next 60 min: {len(live_trips) + len(scheduled_trips)}")
        print(f"  Live (with delay): {len(live_trips)} ({len(live_trips)/(len(live_trips)+len(scheduled_trips))*100:.1f}%)" if (live_trips + scheduled_trips) else "  Live (with delay): 0")
        print(f"  Scheduled only: {len(scheduled_trips)} ({len(scheduled_trips)/(len(live_trips)+len(scheduled_trips))*100:.1f}%)" if (live_trips + scheduled_trips) else "  Scheduled only: 0")
        
        if len(live_trips) == 0:
            print(f"\n⚠️  CONCLUSION:")
            print(f"  The STM GTFS-Realtime feed does NOT appear to include delay data.")
            print(f"  All trips are scheduled times only, even though they're in the real-time feed.")
            print(f"  This means all departures will show as 'scheduled' (black) in the UI.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_all_live_data()

