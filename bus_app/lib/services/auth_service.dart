import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_user.dart';

const String _baseUrl = String.fromEnvironment(
  'BOOKUTU_API_URL',
  defaultValue: 'http://10.0.2.2:4000',
);
const String _apiUrl = '$_baseUrl/api/v1';
const String _registerEndpoint = '$_apiUrl/auth/register';
const String _loginEndpoint = '$_apiUrl/auth/login';

class AuthService {
  Future<AppUser> registerUser({
    required String firstName,
    required String lastName,
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
    String? phoneNumber,
  }) async {
    final url = Uri.parse(_registerEndpoint);
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
        if (phoneNumber != null && phoneNumber.isNotEmpty) 'phoneNumber': phoneNumber,
      }),
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode == 201) {
      await _saveSession(data, email);
      return AppUser.fromJson(data['user'] as Map<String, dynamic>);
    }

    throw Exception(data['message'] ?? 'Registration failed');
  }

  Future<AppUser> loginUser({
    required String email,
    required String password,
  }) async {
    final url = Uri.parse(_loginEndpoint);
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
      return AppUser.fromJson(data['user'] as Map<String, dynamic>);
    }

    throw Exception(data['message'] ?? 'Login failed');
  }

  Future<void> logoutUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('email');
    await prefs.remove('username');
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');
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

  Future<AppUser?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString('user_data');
    if (userDataString == null) {
      return null;
    }

    return AppUser.fromJson(jsonDecode(userDataString) as Map<String, dynamic>);
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
