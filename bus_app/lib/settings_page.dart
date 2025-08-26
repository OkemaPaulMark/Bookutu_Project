import 'package:flutter/material.dart';

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
            _buildTile(Icons.person, 'Profile', 'Edit your profile', () {}),
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
              trailing: Switch(
                value: true, // Replace with state management
                onChanged: (value) {},
              ),
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
            title: const Text(
              'Logout',
              style: TextStyle(color: Colors.red),
            ),
            tileColor: Colors.red.shade50,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            onTap: () {},
          ),
        ],
      ),
    );
  }

  // Helper to build section headers
  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
    );
  }

  // Helper to build list tiles with optional subtitle
  Widget _buildTile(IconData icon, String title, String? subtitle, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      onTap: onTap,
    );
  }

  // Helper to return a ListView.separated wrapped in a Column
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
