import 'package:bus_app/main.dart';
import 'package:flutter/material.dart';
import 'services/auth_service.dart'; // adjust path if needed

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final AuthService _authService = AuthService();

  String username = '';
  String email = '';
  String password = '';
  String confirmPassword = '';
  String error = '';
  bool loading = false;

void _register() async {
  if (_formKey.currentState!.validate()) {
    setState(() {
      loading = true;
      error = '';
    });

    final result = await _authService.registerUser(
      username: username,
      email: email,
      password: password,
      confirmPassword: confirmPassword,
    );

    setState(() {
      loading = false;
      error = result['message'];
    });

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'])),
      );

      // Navigate to DefaultPage like login
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const DefaultPage()),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'] ?? 'Registration failed')),
      );
    }
  }
}


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Register")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: ListView(
                  children: [
                    TextFormField(
                      decoration: const InputDecoration(labelText: "Username"),
                      validator: (val) => val == null || val.isEmpty ? 'Enter username' : null,
                      onChanged: (val) => setState(() => username = val),
                    ),
                    TextFormField(
                      decoration: const InputDecoration(labelText: "Email"),
                      validator: (val) => val == null || !val.contains('@') ? 'Enter a valid email' : null,
                      onChanged: (val) => setState(() => email = val),
                    ),
                    TextFormField(
                      decoration: const InputDecoration(labelText: "Password"),
                      obscureText: true,
                      validator: (val) => val != null && val.length < 6 ? 'Enter min 6 chars' : null,
                      onChanged: (val) => setState(() => password = val),
                    ),
                    TextFormField(
                      decoration: const InputDecoration(labelText: "Confirm Password"),
                      obscureText: true,
                      validator: (val) => val != password ? 'Passwords don’t match' : null,
                      onChanged: (val) => setState(() => confirmPassword = val),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _register,
                      child: const Text("Register"),
                    ),
                    if (error.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Text(error, style: const TextStyle(color: Colors.red)),
                      ),
                  ],
                ),
              ),
            ),
    );
  }
}
