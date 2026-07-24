import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/auth_controller.dart';
import '../views/sign_in_view.dart';
import '../views/main_shell.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthController()..loadSession()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Bookutu',
        home: const _AuthGate(),
      ),
    );
  }
}

class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    final authController = context.watch<AuthController>();

    if (authController.isInitializing) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return authController.isLoggedIn ? const DefaultPage() : const SignInScreen();
  }
}
