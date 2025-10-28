import requests
import random
import string
import json

# Base URL of your Django application
BASE_URL = 'http://localhost:8001'

def generate_random_username():
    """Generate a random username to avoid conflicts"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"testuser_{random_string}"

def generate_random_email():
    """Generate a random email to avoid conflicts"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_mobile_registration():
    """Test mobile user registration with unique data"""
    url = f'{BASE_URL}/api/auth/register/'  # Adjust if your URL is different
    
    # Generate unique test data
    username = generate_random_username()
    email = generate_random_email()
    
    test_data = {
        "username": username,
        "email": email,
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    print(f"Testing with username: {username}")
    print(f"Testing with email: {email}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            print(f"Response: {response.json()}")
            return {
                "username": username,
                "email": email,
                "password": "SecurePassword123",
                "user_data": response.json()
            }
        else:
            print("❌ Registration failed!")
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_mobile_login(credentials):
    """Test mobile user login"""
    if not credentials:
        print("Skipping login test - no valid credentials")
        return None
        
    url = f'{BASE_URL}/api/auth/login/'  # Adjust if your URL is different
    
    login_data = {
        "username": credentials["username"],
        "password": credentials["password"]
    }
    
    print(f"\nTesting login with username: {credentials['username']}")
    
    try:
        response = requests.post(url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            response_data = response.json()
            print(f"Access Token: {response_data.get('access', 'Not found')[:50]}...")
            print(f"User Info: {response_data.get('user', {})}")
            return response_data
        else:
            print("❌ Login failed!")
            print(f"Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_protected_endpoint(access_token):
    """Test accessing a protected endpoint"""
    if not access_token:
        print("Skipping protected endpoint test - no access token")
        return
        
    url = f'{BASE_URL}/accounts/api/profile/'  # Adjust based on your available endpoints
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\nTesting protected endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
            print(f"Response: {response.json()}")
        else:
            print("❌ Protected endpoint access failed!")
            print(f"Error: {response.json()}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def run_tests():
    """Run all tests"""
    print("🚀 Testing Mobile Authentication Endpoints")
    print("=" * 50)
    
    # Test registration
    print("\n1. Testing Mobile User Registration...")
    credentials = test_mobile_registration()
    
    if not credentials:
        print("❌ Cannot proceed with tests due to registration failure")
        return
    
    # Test login
    print("\n2. Testing Mobile User Login...")
    login_response = test_mobile_login(credentials)
    
    if login_response:
        # Test protected endpoint
        print("\n3. Testing Protected Endpoint Access...")
        access_token = login_response.get('access')
        test_protected_endpoint(access_token)
        
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Tests failed at login stage")

if __name__ == "__main__":
    run_tests()