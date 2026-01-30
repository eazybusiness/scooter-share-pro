"""
Simple test script to check ratings in production
"""

import requests
import json

# Base URL
BASE_URL = "https://scooter-share-pro.onrender.com"

# Login as admin
login_data = {
    "email": "admin@scootershare.com",
    "password": "Admin123!"
}

print("Logging in as admin...")
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

if response.status_code == 200:
    auth_data = response.json()
    access_token = auth_data["access_token"]
    print(f"Login successful! User ID: {auth_data['user']['id']}")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Try to get rentals
    print("\nTrying to get rentals...")
    response = requests.get(f"{BASE_URL}/api/rentals", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    # If that fails, try getting a specific rental
    if response.status_code == 404:
        print("\nTrying different endpoints...")
        
        # Try rental detail for ID 13
        response = requests.get(f"{BASE_URL}/api/rentals/13", headers=headers)
        print(f"GET /api/rentals/13 - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Rental 13 - Rating: {data.get('rating')}, Feedback: {data.get('feedback')}")
        
        # Try rental detail for ID 14
        response = requests.get(f"{BASE_URL}/api/rentals/14", headers=headers)
        print(f"GET /api/rentals/14 - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Rental 14 - Rating: {data.get('rating')}, Feedback: {data.get('feedback')}")
    
    # Try debug endpoints if deployment is done
    print("\nTrying debug endpoint...")
    response = requests.get(f"{BASE_URL}/api/debug/ratings", headers=headers)
    print(f"GET /api/debug/ratings - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Debug data: {json.dumps(data, indent=2)}")
    
else:
    print(f"Login failed: {response.status_code} - {response.text}")
