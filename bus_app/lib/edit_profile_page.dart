import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'services/api_service.dart';

class EditProfilePage extends StatefulWidget {
  const EditProfilePage({super.key});

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  final _first = TextEditingController();
  final _last = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  bool loading = true;
  bool saving = false;
  String? error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final p = await ApiService.profile();
      _first.text = p['first_name'] ?? '';
      _last.text = p['last_name'] ?? '';
      _email.text = p['email'] ?? '';
      _phone.text = p['phone_number'] ?? '';
    } catch (e) {
      error = e.toString();
    }
    if (mounted) setState(() => loading = false);
  }

  Future<void> _save() async {
    setState(() => saving = true);
    try {
      final p = await ApiService.updateProfile({
        'first_name': _first.text.trim(),
        'last_name': _last.text.trim(),
        'phone_number': _phone.text.trim(),
      });
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('username', p['first_name'] ?? '');
      await prefs.setString('user_data', jsonEncode(p));
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profile saved!')));
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  void dispose() {
    for (final c in [_first, _last, _email, _phone]) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final initials = '${_first.text.isNotEmpty ? _first.text[0] : ''}'
            '${_last.text.isNotEmpty ? _last.text[0] : ''}'
        .toUpperCase();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile', style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error != null
              ? Center(child: Text(error!))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: context.brand.withOpacity(0.2),
                        child: Text(initials.isEmpty ? '?' : initials,
                            style: TextStyle(fontSize: 32, color: context.brand)),
                      ),
                      const SizedBox(height: 24),
                      _field(_first, 'First name'),
                      _field(_last, 'Last name'),
                      _field(_email, 'Email', enabled: false),
                      _field(_phone, 'Phone number', keyboard: TextInputType.phone),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: saving ? null : _save,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue.shade900,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: Text(saving ? 'Saving…' : 'Save Changes',
                              style: const TextStyle(color: Colors.white, fontSize: 16)),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _field(TextEditingController c, String label,
      {bool enabled = true, TextInputType? keyboard}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: c,
        enabled: enabled,
        keyboardType: keyboard,
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
      ),
    );
  }
}
