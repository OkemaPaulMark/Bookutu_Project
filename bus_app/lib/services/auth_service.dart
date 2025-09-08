import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final String baseUrl = 'http://10.10.132.20:8000/api'; // Updated IP address

  Future<Map<String, dynamic>> registerUser({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    final url = Uri.parse('$baseUrl/register/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirmPassword,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return {'success': true, 'message': 'Registration successful'};
    } else {
      return {
        'success': false,
        'message': data['error'] ?? 'Registration failed'
      };
    }
  }

  Future<Map<String, dynamic>> loginUser({
    required String username,
    required String password,
  }) async {
    final url = Uri.parse('$baseUrl/login/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      // Save the username and token to SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('username', username);
      if (data.containsKey('token')) {
        await prefs.setString('token', data['token']);
      }

      return {'success': true, 'message': 'Login successful', 'data': data};
    } else {
      return {'success': false, 'message': data['error'] ?? 'Login failed'};
    }
  }

  Future<Map<String, dynamic>> logoutUser() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    // Always clear local user data, regardless of backend logout success
    await prefs.remove('username');
    await prefs.remove('token');

    if (token == null) {
      return {
        'success':
            true, // Treat as success from client perspective if no token was there
        'message': 'Logged out successfully from device.',
      };
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/logout/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': 'Logged out successfully.',
        };
      } else {
        // Even if backend logout fails, we've cleared local data
        return {
          'success': true,
          'message':
              'Logged out from device, but backend logout failed. Please try again.',
        };
      }
    } catch (e) {
      // Handle network errors during backend logout
      return {
        'success': true,
        'message':
            'Logged out from device, but network error during backend logout.',
      };
    }
  }
}
