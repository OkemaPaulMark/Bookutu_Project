import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:bus_app/edit_profile_page.dart';
import 'package:bus_app/login_screen.dart';
import 'package:bus_app/notification.dart';
import 'package:bus_app/bookings_page.dart';
import 'package:bus_app/services/auth_service.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  void _soon(BuildContext context, String what) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('$what is coming soon')));
  }

  void _chooseTheme(BuildContext context, ThemeMode current) {
    showDialog(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Appearance'),
        children: [
          for (final (m, label) in [
            (ThemeMode.system, 'System default'),
            (ThemeMode.light, 'Light'),
            (ThemeMode.dark, 'Dark'),
          ])
            ListTile(
              leading: Icon(m == current ? Icons.radio_button_checked : Icons.radio_button_off),
              title: Text(label),
              onTap: () {
                ThemeController.set(m);
                Navigator.pop(ctx);
              },
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings', style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSectionTitle('Account Settings'),
          _buildSeparatedList([
            _buildTile(Icons.person, 'Profile', 'Edit your profile', () {
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const EditProfilePage()),
              );
            }),
            _buildTile(Icons.confirmation_number, 'My Bookings', 'Tickets, payments & cancellations', () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const BookingsPage()));
            }),
            _buildTile(Icons.lock, 'Change Password', 'Update your password',
                () => _soon(context, 'Change password')),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Preferences'),
          _buildSeparatedList([
            _buildTile(Icons.notifications, 'Notifications',
                'View your notifications', () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const NotificationScreen()));
            }),
            _buildTile(Icons.language, 'Language', 'Change app language',
                () => _soon(context, 'Language selection')),
            ValueListenableBuilder<ThemeMode>(
              valueListenable: ThemeController.mode,
              builder: (context, mode, _) => ListTile(
                leading: Icon(context.isDark ? Icons.dark_mode : Icons.light_mode),
                title: const Text('Dark Mode'),
                subtitle: Text(const {
                  ThemeMode.system: 'Following system setting',
                  ThemeMode.light: 'Always light',
                  ThemeMode.dark: 'Always dark',
                }[mode]!),
                onTap: () => _chooseTheme(context, mode),
                trailing: Switch(
                  value: context.isDark,
                  onChanged: (v) => ThemeController.set(v ? ThemeMode.dark : ThemeMode.light),
                ),
              ),
            ),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Security & Privacy'),
          _buildSeparatedList([
            _buildTile(Icons.privacy_tip, 'Privacy Settings',
                'Manage data sharing & tracking', () => _soon(context, 'Privacy settings')),
            _buildTile(Icons.security, 'App Permissions',
                'Control app access to resources', () => _soon(context, 'Permission settings')),
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Support'),
          _buildSeparatedList([
            _buildTile(Icons.help, 'Help & Support', 'support@bookutu.com • +256 700 000 000', () {
              showDialog(
                context: context,
                builder: (_) => const AlertDialog(
                  title: Text('Help & Support'),
                  content: Text('Email: support@bookutu.com\nPhone: +256 700 000 000\n\n'
                      'For a booking issue, quote the Ticket ID shown on your ticket.'),
                ),
              );
            }),
            _buildTile(Icons.feedback, 'Send Feedback', null, () => _soon(context, 'In-app feedback')),
            _buildTile(Icons.info, 'About', null, () {
              showAboutDialog(
                context: context,
                applicationName: 'Bookutu',
                applicationVersion: '1.0.0',
                applicationLegalese: 'Book bus tickets across Uganda.',
              );
            }),
          ]),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text(
              'Logout',
              style: TextStyle(color: Colors.red),
            ),
            tileColor: Colors.red.withOpacity(0.1),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            onTap: () async {
              await AuthService().logoutUser();
              if (!context.mounted) return;
              Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const SignInScreen()),
                (_) => false,
              );
            },
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
  Widget _buildTile(
      IconData icon, String title, String? subtitle, VoidCallback onTap) {
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
