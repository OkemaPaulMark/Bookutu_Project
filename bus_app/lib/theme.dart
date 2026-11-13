import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

const brandBlue = Color(0xFF0D47A1); // Colors.blue.shade900

/// App-wide theme mode, persisted across launches.
class ThemeController {
  ThemeController._();
  static final mode = ValueNotifier<ThemeMode>(ThemeMode.system);
  static const _key = 'theme_mode';

  static Future<void> load() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      mode.value = ThemeMode.values.firstWhere(
        (m) => m.name == prefs.getString(_key),
        orElse: () => ThemeMode.system,
      );
    } catch (_) {}
  }

  static Future<void> set(ThemeMode m) async {
    mode.value = m;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_key, m.name);
    } catch (_) {}
  }

  /// Toggle between explicit light and dark, based on what is showing now.
  static Future<void> toggle(BuildContext context) =>
      set(context.isDark ? ThemeMode.light : ThemeMode.dark);
}

ThemeData buildTheme(Brightness brightness) {
  final dark = brightness == Brightness.dark;
  final scheme = ColorScheme.fromSeed(seedColor: brandBlue, brightness: brightness);
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    brightness: brightness,
    scaffoldBackgroundColor: dark ? const Color(0xFF0F1419) : Colors.white,
    cardColor: dark ? const Color(0xFF1A2129) : Colors.white,
    cardTheme: CardThemeData(color: dark ? const Color(0xFF1A2129) : Colors.white),
    appBarTheme: AppBarTheme(
      backgroundColor: dark ? const Color(0xFF0A2A5E) : brandBlue,
      foregroundColor: Colors.white,
      iconTheme: const IconThemeData(color: Colors.white),
      titleTextStyle: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w500),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: dark ? const Color(0xFF141A21) : Colors.white,
      selectedItemColor: dark ? Colors.blue.shade200 : brandBlue,
      unselectedItemColor: Colors.grey,
    ),
    drawerTheme: DrawerThemeData(backgroundColor: dark ? const Color(0xFF141A21) : Colors.white),
    dividerColor: dark ? Colors.white12 : Colors.black12,
  );
}

extension ThemeX on BuildContext {
  bool get isDark => Theme.of(this).brightness == Brightness.dark;

  /// Brand colour for text/icons: dark navy on light, soft blue on dark.
  Color get brand => isDark ? Colors.blue.shade200 : brandBlue;

  /// Background for list pages (slightly off the card colour).
  Color get pageBg => isDark ? const Color(0xFF0F1419) : Colors.grey.shade100;

  /// Raised surfaces: cards, sheets, ticket panels.
  Color get surface => Theme.of(this).cardColor;

  /// Filled text-field background.
  Color get fieldFill => isDark ? const Color(0xFF222B35) : Colors.grey.shade100;

  /// Secondary text.
  Color get muted => isDark ? Colors.grey.shade400 : Colors.grey.shade700;

  Color get shadow => isDark ? Colors.black54 : Colors.grey.shade300;
}
