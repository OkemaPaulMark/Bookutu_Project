import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final String baseUrl = 'http://10.10.132.24:8000/api';

  Future<Map<String, dynamic>> registerUser({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    final url = Uri.parse('$baseUrl/register/');
    final Map<String, dynamic> requestBody = {
      'username': username,
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
    };

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(requestBody),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return {
        'success': true,
        'message': data['message'] ?? 'Registration successful',
        'user': data['user']
      };
    } else {
      // Handle field-specific errors
      String errorMessage = 'Registration failed';
      if (data.containsKey('email') && data['email'] is List) {
        errorMessage = data['email'][0];
      } else if (data.containsKey('phone_number') && data['phone_number'] is List) {
        errorMessage = data['phone_number'][0];
      } else if (data.containsKey('password') && data['password'] is List) {
        errorMessage = data['password'][0];
      } else if (data.containsKey('non_field_errors') && data['non_field_errors'] is List) {
        errorMessage = data['non_field_errors'][0];
      }
      return {'success': false, 'message': errorMessage};
    }
  }

  Future<Map<String, dynamic>> loginUser({
    required String email,
    required String password,
  }) async {
    final url = Uri.parse('$baseUrl/login/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      // Save tokens and user data to SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('email', email);
      await prefs.setString('username', data['user']['username']);
      await prefs.setString('access_token', data['access']);
      await prefs.setString('refresh_token', data['refresh']);
      await prefs.setString('user_data', jsonEncode(data['user']));

      return {
        'success': true,
        'message': 'Login successful',
        'data': data,
        'user': data['user']
      };
    } else {
      // Handle field-specific errors
      String errorMessage = 'Login failed';
      if (data.containsKey('non_field_errors') && data['non_field_errors'] is List) {
        errorMessage = data['non_field_errors'][0];
      }
      return {'success': false, 'message': errorMessage};
    }
  }

  Future<Map<String, dynamic>> logoutUser() async {
    final prefs = await SharedPreferences.getInstance();
    final accessToken = prefs.getString('access_token');

    // Always clear local user data, regardless of backend logout success
    await prefs.remove('email');
    await prefs.remove('username');
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');

    if (accessToken == null) {
      return {
        'success': true,
        'message': 'Logged out successfully from device.',
      };
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/logout/'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': 'Logged out successfully.',
        };
      } else {
        return {
          'success': true,
          'message': 'Logged out from device.',
        };
      }
    } catch (e) {
      return {
        'success': true,
        'message': 'Logged out from device.',
      };
    }
  }

  // Helper methods for token management
  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('refresh_token');
  }

  Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString('user_data');
    if (userDataString != null) {
      return jsonDecode(userDataString);
    }
    return null;
  }

  Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    return token != null;
  }

  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('username');
  }

  Future<String?> getEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('email');
  }
}
