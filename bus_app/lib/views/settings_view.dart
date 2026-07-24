import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/auth_controller.dart';
import 'sign_in_view.dart';
import 'edit_profile_view.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: Colors.blue.shade900,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSectionTitle('Account Settings'),
          _buildSeparatedList([
            _buildTile(Icons.person, 'Profile', 'Edit your profile', () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const EditProfilePage()),
              );
            }),
            _buildTile(Icons.lock, 'Change Password', 'Update your password', () {}),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Preferences'),
          _buildSeparatedList([
            _buildTile(Icons.notifications, 'Notifications', 'Manage notification settings', () {}),
            _buildTile(Icons.language, 'Language', 'Change app language', () {}),
            ListTile(
              leading: const Icon(Icons.dark_mode),
              title: const Text('Dark Mode'),
              trailing: Switch(value: false, onChanged: (value) {}),
            ),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Security & Privacy'),
          _buildSeparatedList([
            _buildTile(Icons.privacy_tip, 'Privacy Settings', 'Manage data sharing & tracking', () {}),
            _buildTile(Icons.security, 'App Permissions', 'Control app access to resources', () {}),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Support'),
          _buildSeparatedList([
            _buildTile(Icons.help, 'Help & Support', null, () {}),
            _buildTile(Icons.feedback, 'Send Feedback', null, () {}),
            _buildTile(Icons.info, 'About', null, () {}),
          ]),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Logout', style: TextStyle(color: Colors.red)),
            tileColor: Colors.red.shade50,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            onTap: () async {
              await context.read<AuthController>().logout();
              if (!context.mounted) return;
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const SignInScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold));
  }

  Widget _buildTile(IconData icon, String title, String? subtitle, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      onTap: onTap,
    );
  }

  Widget _buildSeparatedList(List<Widget> tiles) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemBuilder: (_, index) => tiles[index],
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemCount: tiles.length,
    );
  }
}
