import 'package:flutter/foundation.dart';

import '../services/auth_service.dart';

class EditProfileController extends ChangeNotifier {
  final AuthService _authService;

  EditProfileController({AuthService? authService}) : _authService = authService ?? AuthService();

  String name = '';
  String email = '';
  bool isLoading = true;

  Future<void> loadProfile() async {
    final user = await _authService.getUserData();
    name = user?.username ?? 'User';
    email = user?.email ?? '';
    isLoading = false;
    notifyListeners();
  }
}
