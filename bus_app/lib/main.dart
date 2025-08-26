import 'package:bus_app/splash_screen.dart';
import 'package:flutter/material.dart';
import 'home_page.dart';
import 'book_page.dart';
import 'location_page.dart';
import 'settings_page.dart';

void main() async {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Bookutu',
      home: SplashScreen(),
    );
  }
}

class DefaultPage extends StatefulWidget {
  const DefaultPage({super.key});

  @override
  State<DefaultPage> createState() => _DefaultPageState();
}

class _DefaultPageState extends State<DefaultPage> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
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
      backgroundColor: Colors.white, // Background color of the navigation bar
      selectedItemColor: Colors.blue.shade900, // Color of selected item
      unselectedItemColor: Colors.grey, // Color of unselected items
      selectedLabelStyle: TextStyle(fontWeight: FontWeight.bold), // Selected label style
      unselectedLabelStyle: TextStyle(fontWeight: FontWeight.normal), // Unselected label style
      showSelectedLabels: true, // Always show selected label
      showUnselectedLabels: true, // Show labels for unselected items
      type: BottomNavigationBarType.fixed, // Important if you have more than 3 items
      items: const [
        BottomNavigationBarItem(
          label: 'Home',
          icon: Icon(Icons.home),
        ),
        BottomNavigationBarItem(
          label: 'Book',
          icon: Icon(Icons.directions_bus),
        ),
        BottomNavigationBarItem(
          label: 'Location',
          icon: Icon(Icons.map),
        ),
             BottomNavigationBarItem( // New Settings item
            label: 'Settings',
            icon: Icon(Icons.settings),
          ),
      ],
    ),
    );
  }
}

