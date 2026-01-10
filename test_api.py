#!/usr/bin/env python3
"""
Scooter Share Pro API Test Script
Tests all API endpoints for functionality and error handling
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://scooter-share-pro.onrender.com"
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response, test_name):
    """Print formatted response"""
    print(f"📡 Status: {response.status_code}")
    try:
        data = response.json()
        print(f"📄 Response: {json.dumps(data, indent=2)}")
    except:
        print(f"📄 Response: {response.text}")
    
    if response.status_code < 400:
        print(f"✅ {test_name} - PASSED")
    else:
        print(f"❌ {test_name} - FAILED")

def test_api_docs():
    """Test API documentation endpoint"""
    print_test_header("API Documentation")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/")
        print_response(response, "API Documentation")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Documentation - FAILED: {e}")
        return False

def test_health_check():
    """Test API health check (if available)"""
    print_test_header("Health Check")
    
    try:
        # Try to get available scooters as health check
        response = requests.get(f"{API_BASE}/scooters/available")
        print_response(response, "Health Check (Available Scooters)")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check - FAILED: {e}")
        return False

def test_register():
    """Test user registration endpoint"""
    print_test_header("User Registration")
    
    # Generate unique email for testing
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    
    register_data = {
        "email": test_email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        print_response(response, "User Registration")
        
        if response.status_code == 201:
            data = response.json()
            # Store credentials for login test
            global test_credentials
            test_credentials = {
                "email": test_email,
                "password": "testpassword123"
            }
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ User Registration - FAILED: {e}")
        return False

def test_login():
    """Test API login endpoint"""
    print_test_header("API Login")
    
    if 'test_credentials' not in globals():
        print("❌ No test credentials available - skipping login test")
        return False
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=test_credentials)
        print_response(response, "API Login")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            return None
    except Exception as e:
        print(f"❌ API Login - FAILED: {e}")
        return None

def test_invalid_login():
    """Test API login with invalid credentials"""
    print_test_header("Invalid Login")
    
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        print_response(response, "Invalid Login")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Invalid Login - FAILED: {e}")
        return False

def test_get_scooters(token):
    """Test get all scooters endpoint"""
    print_test_header("Get All Scooters")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/scooters/", headers=headers)
        print_response(response, "Get All Scooters")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get All Scooters - FAILED: {e}")
        return False

def test_get_available_scooters(token):
    """Test get available scooters endpoint"""
    print_test_header("Get Available Scooters")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/scooters/available", headers=headers)
        print_response(response, "Get Available Scooters")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get Available Scooters - FAILED: {e}")
        return False

def test_get_scooter(token, scooter_id=1):
    """Test get specific scooter endpoint"""
    print_test_header(f"Get Scooter {scooter_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/scooters/{scooter_id}", headers=headers)
        print_response(response, f"Get Scooter {scooter_id}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get Scooter {scooter_id} - FAILED: {e}")
        return False

def test_get_rentals(token):
    """Test get user rentals endpoint"""
    print_test_header("Get User Rentals")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/rentals/", headers=headers)
        print_response(response, "Get User Rentals")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get User Rentals - FAILED: {e}")
        return False

def test_get_rental_stats(token):
    """Test get rental statistics endpoint"""
    print_test_header("Get Rental Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/rentals/statistics", headers=headers)
        print_response(response, "Get Rental Statistics")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get Rental Statistics - FAILED: {e}")
        return False

def test_start_rental(token, scooter_id=1):
    """Test start rental endpoint"""
    print_test_header("Start Rental")
    
    headers = {"Authorization": f"Bearer {token}"}
    rental_data = {
        "scooter_id": scooter_id,
        "start_latitude": 47.3769,
        "start_longitude": 8.5417
    }
    
    try:
        response = requests.post(f"{API_BASE}/rentals/", json=rental_data, headers=headers)
        print_response(response, "Start Rental")
        
        if response.status_code == 201:
            data = response.json()
            return data.get('id')
        return None
    except Exception as e:
        print(f"❌ Start Rental - FAILED: {e}")
        return None

def test_get_user_profile(token):
    """Test get user profile endpoint"""
    print_test_header("Get User Profile")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/users/me", headers=headers)
        print_response(response, "Get User Profile")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get User Profile - FAILED: {e}")
        return False

def test_unauthorized_access():
    """Test API access without token"""
    print_test_header("Unauthorized Access")
    
    try:
        response = requests.get(f"{API_BASE}/scooters/")
        print_response(response, "Unauthorized Access")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Unauthorized Access - FAILED: {e}")
        return False

def test_invalid_endpoint():
    """Test invalid API endpoint"""
    print_test_header("Invalid Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/invalid")
        print_response(response, "Invalid Endpoint")
        return response.status_code == 404
    except Exception as e:
        print(f"❌ Invalid Endpoint - FAILED: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Scooter Share Pro API Test Suite")
    print(f"🌐 Testing against: {BASE_URL}")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test basic endpoints
    results.append(("API Documentation", test_api_docs()))
    results.append(("Health Check", test_health_check()))
    results.append(("Invalid Endpoint", test_invalid_endpoint()))
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # Test authentication
    results.append(("Invalid Login", test_invalid_login()))
    registration_success = test_register()
    results.append(("User Registration", registration_success))
    
    token = None
    if registration_success:
        token = test_login()
        results.append(("API Login", token is not None))
    
    if token:
        # Test authenticated endpoints
        results.append(("Get All Scooters", test_get_scooters(token)))
        results.append(("Get Available Scooters", test_get_available_scooters(token)))
        results.append(("Get Specific Scooter", test_get_scooter(token)))
        results.append(("Get User Rentals", test_get_rentals(token)))
        results.append(("Get Rental Statistics", test_get_rental_stats(token)))
        results.append(("Get User Profile", test_get_user_profile(token)))
        
        # Test rental operations
        rental_id = test_start_rental(token)
        results.append(("Start Rental", rental_id is not None))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is ready for production.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
