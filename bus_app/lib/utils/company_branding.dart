import 'package:flutter/material.dart';

// Deterministic per-company color, since companies don't have a real logo/brand
// color on file yet. Same company name always maps to the same color.
class CompanyBranding {
  static const List<Color> _palette = [
    Color(0xFF1D4ED8), // blue
    Color(0xFF047857), // emerald
    Color(0xFFB91C1C), // red
    Color(0xFF7C3AED), // violet
    Color(0xFFC2410C), // orange
    Color(0xFF0E7490), // cyan
    Color(0xFFA21CAF), // fuchsia
    Color(0xFF4D7C0F), // lime green
    Color(0xFFBE185D), // pink
    Color(0xFF0F766E), // teal
  ];

  static Color colorFor(String companyName) {
    if (companyName.isEmpty || companyName == 'N/A') return Colors.blue.shade900;
    final hash = companyName.codeUnits.fold<int>(0, (sum, code) => sum + code);
    return _palette[hash % _palette.length];
  }
}
