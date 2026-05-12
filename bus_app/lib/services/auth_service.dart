import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class AuthService {
  Future<Map<String, dynamic>> registerUser({
    required String firstName,
    required String lastName,
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    final url = Uri.parse(AppConfig.registerEndpoint);
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firstName': firstName,
        'lastName': lastName,
        'username': username,
        'email': email,
        'password': password,
        'confirmPassword': confirmPassword,
      }),
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode == 201) {
      await _saveSession(data, email);
      return {
        'success': true,
        'message': 'Registration successful',
        'user': data['user'],
      };
    }

    return {
      'success': false,
      'message': data['message'] ?? 'Registration failed',
    };
  }

  Future<Map<String, dynamic>> loginUser({
    required String email,
    required String password,
  }) async {
    final url = Uri.parse(AppConfig.loginEndpoint);
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode == 200) {
      await _saveSession(data, email);
      return {
        'success': true,
        'message': 'Login successful',
        'data': data,
        'user': data['user'],
      };
    }

    return {
      'success': false,
      'message': data['message'] ?? 'Login failed',
    };
  }

  Future<Map<String, dynamic>> logoutUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('email');
    await prefs.remove('username');
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');

    return {
      'success': true,
      'message': 'Logged out successfully from device.',
    };
  }

  Future<void> _saveSession(Map<String, dynamic> data, String email) async {
    final prefs = await SharedPreferences.getInstance();
    final user = data['user'] as Map<String, dynamic>;
    final username = user['username'] as String? ?? '';

    await prefs.setString('email', email);
    await prefs.setString('username', username);
    await prefs.setString('access_token', data['access'] as String);
    await prefs.setString('refresh_token', data['refresh'] as String);
    await prefs.setString('user_data', jsonEncode(user));
  }

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
    if (userDataString == null) {
      return null;
    }

    return jsonDecode(userDataString) as Map<String, dynamic>;
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
