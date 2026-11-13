import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'main.dart';
import 'login_screen.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _route();
  }

  Future<void> _route() async {
    final results = await Future.wait([
      AuthService().isLoggedIn(),
      Future.delayed(const Duration(seconds: 2), () => true),
    ]);
    if (!mounted) return;
    var loggedIn = results[0];
    if (loggedIn) {
      // Make sure the saved session is still valid (refreshes it if expired).
      try {
        await ApiService.profile();
      } on AuthRequiredException {
        loggedIn = false;
      } catch (_) {
        // Offline/server down: let the user in; screens show their own errors.
      }
      if (!mounted) return;
    }
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => loggedIn ? const DefaultPage() : const SignInScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue.shade900,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              height: 100,
              width: 100,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text(
                  '🚌',
                  style: TextStyle(fontSize: 40),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Bookutu',
              style: TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Your best travel buddy',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 40),
            const SpinKitFadingCircle(
              color: Colors.white,
              size: 40.0,
            ),
          ],
        ),
      ),
    );
  }
}
