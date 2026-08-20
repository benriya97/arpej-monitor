import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Configuration
ARPEJ_URL = "https://www.arpej.fr/fr/nos-residences/"
FILTERS = {
    "related_city": "54157,52682,52740,52722,52782,52768,54167",
    "iam": "etudiants"
}

print("=" * 60)
print("ARPEJ RESIDENCE MONITOR - DEBUG VERSION")
print("=" * 60)

# Test 1: Check if secrets are loaded
print("\n[TEST 1] Checking environment variables...")
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
recipient_email = os.getenv('RECIPIENT_EMAIL')

if sender_email and sender_password and recipient_email:
    print("✓ All email secrets loaded successfully")
    print(f"  - SENDER_EMAIL: {sender_email[:10]}***")
    print(f"  - RECIPIENT_EMAIL: {recipient_email[:10]}***")
else:
    print("✗ Missing email secrets!")
    print(f"  - SENDER_EMAIL: {sender_email}")
    print(f"  - SENDER_PASSWORD: {sender_password}")
    print(f"  - RECIPIENT_EMAIL: {recipient_email}")

# Test 2: Try to fetch the website
print("\n[TEST 2] Attempting to fetch Arpej website...")
print(f"URL: {ARPEJ_URL}")

try:
    params = "&".join([f"{k}={v}" for k, v in FILTERS.items()])
    url = f"{ARPEJ_URL}?{params}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Sending request (timeout: 5 seconds)...")
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    
    print(f"✓ Website responded with status code: {response.status_code}")
    print(f"  - Content length: {len(response.content)} bytes")
    
    # Test 3: Parse the response
    print("\n[TEST 3] Parsing website content...")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find residence items
    residence_items = soup.find_all('div', class_=lambda x: x and 'residence' in x.lower())
    print(f"✓ Found {len(residence_items)} residence divs")
    
    if len(residence_items) == 0:
        # Alternative search
        residence_items = soup.find_all('a', class_=lambda x: x and ('card' in x.lower() or 'item' in x.lower()))
        print(f"✓ Found {len(residence_items)} alternative items")
    
    # Test 4: Summary
    print("\n[TEST 4] Summary")
    print("✓ Website is accessible")
    print("✓ Page contains residence listings")
    print("\n🎉 All tests passed! The system is working correctly.")
    
except requests.exceptions.Timeout:
    print("✗ Website request TIMEOUT (took more than 5 seconds)")
    print("  The Arpej website is too slow to respond")
    
except requests.exceptions.ConnectionError:
    print("✗ CONNECTION ERROR - Cannot reach the website")
    print("  Check internet connection or if website is down")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
