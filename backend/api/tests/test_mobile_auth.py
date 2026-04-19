"""
Unit tests for mobile authentication endpoints
"""
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class MobileAuthTests(APITestCase):
    """
    Test cases for mobile authentication endpoints
    """

    def setUp(self):
        """Set up test data"""
        self.register_url = reverse('mobile-register')
        self.login_url = reverse('mobile-login')
        self.logout_url = reverse('mobile-logout')

        self.valid_registration_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }

        self.valid_login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        # The response includes user data but username might not be included in the serialized output
        # Let's check the key fields that are present
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['user_type'], 'PASSENGER')

        # Verify user was created in database
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertEqual(user.user_type, 'PASSENGER')

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username fails"""
        # Create first user
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        # Try to create user with same username
        duplicate_data = self.valid_registration_data.copy()
        duplicate_data['email'] = 'different@example.com'

        response = self.client.post(
            self.register_url,
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails"""
        # Create first user
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        # Try to create user with same email
        duplicate_data = self.valid_registration_data.copy()
        duplicate_data['username'] = 'differentuser'

        response = self.client.post(
            self.register_url,
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch fails"""
        invalid_data = self.valid_registration_data.copy()
        invalid_data['confirm_password'] = 'DifferentPass123!'

        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        """Test successful user login"""
        # First register the user
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        # Now login
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        # The response includes user data but username might not be included in the serialized output
        # Let's check the key fields that are present
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['user_type'], 'PASSENGER')

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        # First register the user
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        # Try login with wrong password
        invalid_login_data = {
            'username': 'testuser',
            'password': 'WrongPass123!'
        }

        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user fails"""
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_logout_success(self):
        """Test successful user logout"""
        # Register and login first
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_registration_data),
            content_type='application/json'
        )

        login_response = self.client.post(
            self.login_url,
            data=json.dumps(self.valid_login_data),
            content_type='application/json'
        )

        access_token = login_response.data['access']

        # Now logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logged out successfully.')

    def test_user_logout_without_token(self):
        """Test logout without authentication token fails"""
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registration_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password and confirm_password
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('confirm_password', response.data)

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        incomplete_data = {
            'username': 'testuser'
            # Missing password
        }

        response = self.client.post(
            self.login_url,
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)