#!/usr/bin/env python3
"""
Test script to check STM and BIXI API connectivity
"""

import requests
import json
import sys

def test_bixi_api():
    """Test BIXI GBFS API"""
    print("=" * 60)
    print("Testing BIXI API")
    print("=" * 60)
    
    urls = [
        "https://api-core.bixi.com/gbfs/en/station_status.json",
        "https://gbfs.velobixi.com/gbfs/en/station_status.json",
        "https://bixi.com/data/bikeStations.json",  # Alternative endpoint
    ]
    
    for url in urls:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                stations = data.get('data', {}).get('stations', [])
                print(f"  ✓ SUCCESS! Found {len(stations)} stations")
                if stations:
                    print(f"  First station: ID={stations[0].get('station_id')}, Name={stations[0].get('name', 'N/A')}")
                return url, data
            else:
                print(f"  ✗ Failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {e}")
    
    return None, None

def test_stm_api():
    """Test STM API"""
    print("\n" + "=" * 60)
    print("Testing STM API")
    print("=" * 60)
    
    url = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=10, headers={"Accept": "application/x-protobuf"})
        print(f"  Status Code: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print(f"  ✓ SUCCESS! API is accessible")
            print(f"  Note: This is a protobuf feed, requires special parsing")
            return True
        elif response.status_code == 403:
            print(f"  ⚠ API requires authentication (API key)")
            print(f"  Visit: https://portail.developpeurs.stm.info/apihub")
            return False
        else:
            print(f"  ✗ Failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: {e}")
        return False

def test_backend_endpoints():
    """Test local backend endpoints"""
    print("\n" + "=" * 60)
    print("Testing Local Backend Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    endpoints = [
        "/api/health",
        "/api/bixi",
        "/api/transit",
        "/api/dashboard"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/api/bixi":
                    stations = data.get('stations', [])
                    print(f"  ✓ Found {len(stations)} BIXI stations")
                elif endpoint == "/api/transit":
                    departures = data.get('departures', [])
                    print(f"  ✓ Found {len(departures)} transit departures")
                elif endpoint == "/api/dashboard":
                    print(f"  ✓ Dashboard data retrieved")
                else:
                    print(f"  ✓ {json.dumps(data, indent=2)[:100]}")
            else:
                print(f"  ✗ Failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Backend server not running on port 5001")
            print(f"  Start it with: python3 app.py")
            break
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    print("Home Departure Board - API Connectivity Test")
    print()
    
    # Test external APIs
    bixi_url, bixi_data = test_bixi_api()
    stm_ok = test_stm_api()
    
    # Test backend
    test_backend_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"BIXI API: {'✓ Working' if bixi_url else '✗ Not accessible'}")
    print(f"STM API: {'✓ Accessible (may need API key)' if stm_ok else '✗ Not accessible'}")
    print("\nIf BIXI API is not working, check:")
    print("  1. Internet connectivity")
    print("  2. BIXI API URL may have changed")
    print("  3. Check https://docs.bixi.co/docs for latest API info")
    print("\nIf STM API requires authentication:")
    print("  1. Visit https://portail.developpeurs.stm.info/apihub")
    print("  2. Register and get an API key")
    print("  3. Update app.py to include API key in requests")

