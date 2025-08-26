import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final String baseUrl = 'http://192.168.37.29:8000/api';

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
      return {'success': false, 'message': data['error'] ?? 'Registration failed'};
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
      // Save the username to SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('username', username);

      return {'success': true, 'message': 'Login successful', 'data': data};
    } else {
      return {'success': false, 'message': data['error'] ?? 'Login failed'};
    }
  }

  Future<Map<String, dynamic>> logoutUser() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      return {
        'success': false,
        'message': 'No token found. You are already logged out.',
      };
    }

    final response = await http.post(
      Uri.parse('$baseUrl/logout/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      await prefs.remove('token');
      return {
        'success': true,
        'message': 'Logged out successfully.',
      };
    } else {
      return {
        'success': false,
        'message': 'Logout failed. Please try again.',
      };
    }
  }
}
