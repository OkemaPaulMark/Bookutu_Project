import 'package:flutter/foundation.dart';

import '../models/app_user.dart';
import '../services/auth_service.dart';

class AuthController extends ChangeNotifier {
  final AuthService _authService;

  AuthController({AuthService? authService}) : _authService = authService ?? AuthService();

  bool _isLoading = false;
  bool _isInitializing = true;
  bool _isLoggedIn = false;
  String? _errorMessage;
  AppUser? _currentUser;

  bool get isLoading => _isLoading;
  bool get isInitializing => _isInitializing;
  bool get isLoggedIn => _isLoggedIn;
  String? get errorMessage => _errorMessage;
  AppUser? get currentUser => _currentUser;
  String get username => _currentUser?.username ?? 'User';
  String get email => _currentUser?.email ?? 'user@example.com';

  Future<void> loadSession() async {
    _isLoggedIn = await _authService.isLoggedIn();
    _currentUser = await _authService.getUserData();
    _isInitializing = false;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentUser = await _authService.loginUser(email: email, password: password);
      _isLoggedIn = true;
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> register({
    required String firstName,
    required String lastName,
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
    String? phoneNumber,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentUser = await _authService.registerUser(
        firstName: firstName,
        lastName: lastName,
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
        phoneNumber: phoneNumber,
      );
      _isLoggedIn = true;
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _authService.logoutUser();
    _isLoggedIn = false;
    _currentUser = null;
    notifyListeners();
  }
}
