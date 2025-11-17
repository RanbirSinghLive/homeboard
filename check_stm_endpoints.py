#!/usr/bin/env python3
"""
Check different STM GTFS-Realtime endpoints for live delay data
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

def check_endpoint(url, endpoint_name, api_key):
    """Check a specific STM endpoint for live delay data"""
    print(f"\n{'='*80}")
    print(f"Checking: {endpoint_name}")
    print(f"URL: {url}")
    print('='*80)
    
    headers = {
        'apikey': api_key,
        'Accept': 'application/x-protobuf'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        print(f"✓ Feed downloaded: {len(response.content)} bytes")
        print(f"✓ Entities in feed: {len(feed.entity)}")
        
        # Check what types of entities are in the feed
        entity_types = {
            'trip_update': 0,
            'vehicle': 0,
            'alert': 0,
            'other': 0
        }
        
        live_count = 0
        scheduled_count = 0
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                entity_types['trip_update'] += 1
                trip_update = entity.trip_update
                
                for stop_time_update in trip_update.stop_time_update:
                    has_delay = False
                    if stop_time_update.HasField('arrival'):
                        if stop_time_update.arrival.HasField('delay'):
                            has_delay = True
                            live_count += 1
                        else:
                            scheduled_count += 1
                    elif stop_time_update.HasField('departure'):
                        if stop_time_update.departure.HasField('delay'):
                            has_delay = True
                            live_count += 1
                        else:
                            scheduled_count += 1
            elif entity.HasField('vehicle'):
                entity_types['vehicle'] += 1
            elif entity.HasField('alert'):
                entity_types['alert'] += 1
            else:
                entity_types['other'] += 1
        
        print(f"\nEntity Types:")
        for etype, count in entity_types.items():
            if count > 0:
                print(f"  {etype}: {count}")
        
        if entity_types['trip_update'] > 0:
            print(f"\nDelay Data:")
            print(f"  Live (with delay): {live_count}")
            print(f"  Scheduled (no delay): {scheduled_count}")
            if live_count + scheduled_count > 0:
                pct = (live_count / (live_count + scheduled_count)) * 100
                print(f"  Live percentage: {pct:.1f}%")
        
        return {
            'success': True,
            'entities': len(feed.entity),
            'entity_types': entity_types,
            'live_count': live_count,
            'scheduled_count': scheduled_count
        }
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e.response.status_code}")
        if e.response.status_code == 404:
            print("  Endpoint not found")
        elif e.response.status_code == 403:
            print("  Access forbidden (check API key)")
        return {'success': False, 'error': f'HTTP {e.response.status_code}'}
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'success': False, 'error': str(e)}

def main():
    config = load_config()
    api_key = config.get('transit', {}).get('api_key', '')
    
    if not api_key:
        print("Error: STM API key not found")
        return
    
    # List of known STM GTFS-Realtime endpoints
    endpoints = [
        {
            'name': 'Trip Updates (v2)',
            'url': 'https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates'
        },
        {
            'name': 'Trip Updates (v1)',
            'url': 'https://api.stm.info/pub/od/gtfs-rt/ic/v1/tripUpdates'
        },
        {
            'name': 'Vehicle Positions',
            'url': 'https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions'
        },
        {
            'name': 'Alerts',
            'url': 'https://api.stm.info/pub/od/gtfs-rt/ic/v2/alerts'
        },
        {
            'name': 'Trip Updates (alternative)',
            'url': 'https://api.stm.info/pub/od/gtfs-rt/ic/tripUpdates'
        }
    ]
    
    results = {}
    
    for endpoint in endpoints:
        result = check_endpoint(endpoint['url'], endpoint['name'], api_key)
        results[endpoint['name']] = result
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    for name, result in results.items():
        if result.get('success'):
            live = result.get('live_count', 0)
            scheduled = result.get('scheduled_count', 0)
            total = live + scheduled
            if total > 0:
                pct = (live / total) * 100
                print(f"{name:30} | Entities: {result['entities']:>6} | Live: {live:>4} ({pct:>5.1f}%) | Scheduled: {scheduled:>4}")
            else:
                print(f"{name:30} | Entities: {result['entities']:>6} | No trip updates")
        else:
            print(f"{name:30} | ✗ {result.get('error', 'Failed')}")

if __name__ == '__main__':
    main()

