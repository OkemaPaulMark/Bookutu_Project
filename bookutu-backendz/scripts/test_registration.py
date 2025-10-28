import requests
import json

# Base URL of your Django application
BASE_URL = 'http://localhost:8000'

def test_mobile_registration():
    """Test mobile user registration"""
    url = f'{BASE_URL}/api/mobile/register/'  # Adjust URL based on your actual endpoints
    
    test_data = {
        "username": "testuser_mobile",
        "email": "testmobile@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print("=== Mobile Registration Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Mobile Registration: SUCCESS")
            return response.json()
        else:
            print("❌ Mobile Registration: FAILED")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_web_registration():
    """Test web user registration"""
    url = f'{BASE_URL}/api/register/'  # Adjust URL based on your actual endpoints
    
    test_data = {
        "username": "testuser_web",
        "email": "testweb@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print("\n=== Web Registration Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Web Registration: SUCCESS")
            return response.json()
        else:
            print("❌ Web Registration: FAILED")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    
def test_mobile_login(username, password):
    """Test mobile user login"""
    url = f'{BASE_URL}/api/mobile/login/'  # Adjust URL based on your actual endpoints
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=login_data)
        print("\n=== Mobile Login Test ===")
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        
        if response.status_code == 200:
            print("✅ Mobile Login: SUCCESS")
            print(f"Access Token: {response_data.get('access', 'Not found')[:50]}...")
            print(f"User Info: {response_data.get('user', {})}")
            return response_data
        else:
            print("❌ Mobile Login: FAILED")
            print(f"Error: {response_data}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    
    

def test_web_login(username, password):
    """Test web user login"""
    url = f'{BASE_URL}/api/login/'  # Adjust URL based on your actual endpoints
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=login_data)
        print("\n=== Web Login Test ===")
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        
        if response.status_code == 200:
            print("✅ Web Login: SUCCESS")
            print(f"Access Token: {response_data.get('access', 'Not found')[:50]}...")
            print(f"User Info: {response_data.get('user', {})}")
            return response_data
        else:
            print("❌ Web Login: FAILED")
            print(f"Error: {response_data}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None