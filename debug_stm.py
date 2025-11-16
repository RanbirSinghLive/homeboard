#!/usr/bin/env python3
"""
Debug script to inspect STM GTFS-Realtime feed
"""

import requests
import yaml
import os
from datetime import datetime
from google.transit import gtfs_realtime_pb2

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def debug_stm_feed():
    config = load_config()
    api_key = config.get('transit', {}).get('api_key', '')
    stop_ids = config.get('transit', {}).get('stop_ids', [])
    
    print("=" * 60)
    print("STM GTFS-Realtime Feed Debug")
    print("=" * 60)
    print(f"API Key: {api_key[:10]}...")
    print(f"Looking for stop IDs: {stop_ids}")
    print()
    
    url = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
    headers = {
        'apikey': api_key,
        'Accept': 'application/x-protobuf'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✓ Feed downloaded: {len(response.content)} bytes")
        
        # Parse feed
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        print(f"✓ Feed parsed: {len(feed.entity)} entities")
        print()
        
        # Collect all unique stop IDs in the feed
        all_stop_ids = set()
        stop_ids_with_updates = {}
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                route_id = trip_update.trip.route_id if trip_update.trip.HasField('route_id') else 'N/A'
                
                for stop_time_update in trip_update.stop_time_update:
                    stop_id = stop_time_update.stop_id
                    all_stop_ids.add(stop_id)
                    
                    if stop_id in stop_ids:
                        if stop_id not in stop_ids_with_updates:
                            stop_ids_with_updates[stop_id] = []
                        
                        arrival_time = None
                        if stop_time_update.HasField('arrival'):
                            arrival_time = stop_time_update.arrival.time
                        elif stop_time_update.HasField('departure'):
                            arrival_time = stop_time_update.departure.time
                        
                        if arrival_time:
                            arrival_dt = datetime.fromtimestamp(arrival_time)
                            now = datetime.now()
                            delta = arrival_dt - now
                            minutes = int(delta.total_seconds() / 60)
                            
                            if 0 <= minutes <= 60:
                                stop_ids_with_updates[stop_id].append({
                                    'route': route_id,
                                    'minutes': minutes,
                                    'time': arrival_dt.strftime('%H:%M')
                                })
        
        print(f"Total unique stop IDs in feed: {len(all_stop_ids)}")
        print(f"Sample stop IDs (first 20): {list(sorted(all_stop_ids))[:20]}")
        print()
        
        # Check if our stop IDs are in the feed
        print("Stop ID Analysis:")
        print("-" * 60)
        for stop_id in stop_ids:
            if stop_id in all_stop_ids:
                updates = stop_ids_with_updates.get(stop_id, [])
                print(f"✓ Stop {stop_id}: Found in feed, {len(updates)} upcoming departures")
                if updates:
                    for u in updates[:5]:
                        print(f"    Route {u['route']}: {u['minutes']} min ({u['time']})")
            else:
                print(f"✗ Stop {stop_id}: NOT FOUND in feed")
                # Find closest matches
                stop_id_num = int(stop_id) if stop_id.isdigit() else None
                if stop_id_num:
                    closest = [s for s in all_stop_ids if s.isdigit() and abs(int(s) - stop_id_num) < 10]
                    if closest:
                        print(f"    Closest matches: {sorted(closest)[:5]}")
        
        print()
        print("=" * 60)
        print("Recommendation:")
        if stop_ids_with_updates:
            print("✓ Your stop IDs are in the feed and have departures!")
        else:
            print("⚠ Check if your stop IDs are correct")
            print("  Stop IDs in GTFS-Realtime may differ from static GTFS")
            print("  Try checking the STM website or app for the correct stop codes")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_stm_feed()

