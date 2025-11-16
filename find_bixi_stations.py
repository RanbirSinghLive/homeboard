#!/usr/bin/env python3
"""
Helper script to find BIXI station IDs near your location
"""

import requests
import json
import sys

def find_stations(lat=None, lon=None, search_term=None, limit=20):
    """Find BIXI stations"""
    try:
        response = requests.get("https://gbfs.velobixi.com/gbfs/en/station_information.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        stations = data.get('data', {}).get('stations', [])
        
        print(f"Found {len(stations)} total BIXI stations\n")
        
        # Filter by search term if provided
        if search_term:
            matching = [s for s in stations if search_term.lower() in s.get('name', '').lower()]
            stations = matching
            print(f"Found {len(stations)} stations matching '{search_term}':\n")
        
        # Filter by location if provided
        if lat and lon:
            # Simple distance calculation (rough approximation)
            def distance(s):
                s_lat = s.get('lat', 0)
                s_lon = s.get('lon', 0)
                return ((s_lat - lat)**2 + (s_lon - lon)**2)**0.5
            
            stations.sort(key=distance)
            print(f"Stations nearest to ({lat}, {lon}):\n")
        
        # Display results
        for i, station in enumerate(stations[:limit], 1):
            sid = station.get('station_id')
            name = station.get('name', 'Unknown')
            s_lat = station.get('lat', 0)
            s_lon = station.get('lon', 0)
            capacity = station.get('capacity', 'N/A')
            
            print(f"{i}. {name}")
            print(f"   Station ID: {sid}")
            print(f"   Location: {s_lat}, {s_lon}")
            print(f"   Capacity: {capacity}")
            print()
        
        if len(stations) > limit:
            print(f"... and {len(stations) - limit} more stations")
        
        return stations[:limit]
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("=" * 60)
    print("BIXI Station Finder")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
        print(f"Searching for stations matching: '{search_term}'\n")
        find_stations(search_term=search_term)
    else:
        # Use default location from config or prompt
        print("Usage examples:")
        print("  python3 find_bixi_stations.py 'downtown'")
        print("  python3 find_bixi_stations.py 'metro'")
        print("  python3 find_bixi_stations.py 'park'")
        print()
        print("Or search by location (edit script to add lat/lon)")
        print()
        print("Showing first 20 stations:\n")
        find_stations(limit=20)

