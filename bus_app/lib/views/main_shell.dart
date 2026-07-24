import 'package:flutter/material.dart';

import 'home_view.dart';
import 'location_view.dart';
import 'settings_view.dart';
import 'trip_list_view.dart';

class DefaultPage extends StatefulWidget {
  const DefaultPage({super.key});

  @override
  State<DefaultPage> createState() => _DefaultPageState();
}

class _DefaultPageState extends State<DefaultPage> {
  int _selectedIndex = 0;

  final List<Widget> _pages = const [
    HomePage(),
    BusListScreen(),
    LocationPage(),
    SettingsPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        backgroundColor: Colors.white,
        selectedItemColor: Colors.blue.shade900,
        unselectedItemColor: Colors.grey,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
        unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.normal),
        showSelectedLabels: true,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(label: 'Home', icon: Icon(Icons.home)),
          BottomNavigationBarItem(label: 'Book', icon: Icon(Icons.directions_bus)),
          BottomNavigationBarItem(label: 'Location', icon: Icon(Icons.map)),
          BottomNavigationBarItem(label: 'Settings', icon: Icon(Icons.settings)),
        ],
      ),
    );
  }
}
