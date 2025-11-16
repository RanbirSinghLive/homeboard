#!/usr/bin/env python3
"""
Test STM API with your API key
"""

import requests
import yaml
import os
import sys

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: config.yaml not found at {config_path}")
        return None

def test_stm_api():
    """Test STM API with different header formats"""
    config = load_config()
    if not config:
        return
    
    api_key = config.get('transit', {}).get('api_key', '')
    
    if not api_key:
        print("❌ No API key found in config.yaml")
        print("\nTo add your API key:")
        print("1. Get your API key from https://portail.developpeurs.stm.info/apihub")
        print("2. Add it to config.yaml under transit.api_key")
        return
    
    print("=" * 60)
    print("Testing STM API")
    print("=" * 60)
    print(f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    print()
    
    url = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
    
    # Try different header formats
    header_formats = [
        ('apikey', api_key),
        ('X-API-Key', api_key),
        ('Authorization', f'Bearer {api_key}'),
        ('Authorization', f'ApiKey {api_key}'),
    ]
    
    for header_name, header_value in header_formats:
        print(f"Trying header format: {header_name}")
        headers = {
            header_name: header_value,
            'Accept': 'application/x-protobuf'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS! Using header: {header_name}")
                print(f"  Response size: {len(response.content)} bytes")
                print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                return True
            elif response.status_code == 403:
                print(f"  ❌ Forbidden - Invalid API key or wrong header format")
            elif response.status_code == 401:
                print(f"  ❌ Unauthorized - Check API key")
            else:
                print(f"  ⚠️  Status {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("❌ None of the header formats worked")
    print("\nPossible issues:")
    print("1. API key is incorrect - check in STM portal")
    print("2. API key format is different - check STM API documentation")
    print("3. API key needs to be activated/enabled in the portal")
    print("\nCheck the STM API documentation for the correct header format:")
    print("https://portail.developpeurs.stm.info/apihub")
    
    return False

if __name__ == "__main__":
    test_stm_api()

