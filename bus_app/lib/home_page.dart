import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:url_launcher/url_launcher.dart';


// Import your pages
import 'package:bus_app/edit_profile_page.dart';
import 'package:bus_app/login_screen.dart';
import 'package:bus_app/notification.dart';
import 'package:bus_app/services/auth_service.dart';
import 'package:bus_app/settings_page.dart';
import 'package:bus_app/bookings_page.dart';
import 'package:bus_app/network_test.dart';
import 'package:bus_app/services/notification_service.dart';
import 'package:bus_app/config/app_config.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class Advert {
  final String title;
  final String description;
  final String imageUrl;
  final String? linkUrl;

  Advert({
    required this.title,
    required this.description,
    required this.imageUrl,
    this.linkUrl,
  });

  factory Advert.fromJson(Map<String, dynamic> json) {
    return Advert(
      title: json['title'],
      description: json['description'],
      imageUrl: json['image'], // Make sure API returns full URL
      linkUrl: json['link_url'],
    );
  }
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;
  String username = '';
  String email = '';
  final AuthService _authService = AuthService();
  List<Advert> adverts = [];

  final List<Widget> my_images = [
    Container(
      margin: EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: DecorationImage(
          image: AssetImage('images/bus1.jpg'),
          fit: BoxFit.cover,
        ),
      ),
    ),
    Container(
      margin: EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: DecorationImage(
          image: AssetImage('images/bus2.jpg'),
          fit: BoxFit.cover,
        ),
      ),
    ),
    Container(
      margin: EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: DecorationImage(
          image: AssetImage('images/bus3.jpeg'),
          fit: BoxFit.cover,
        ),
      ),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _loadUserData();
    NetworkTest.testConnection(); // Debug network
    fetchAdverts();
  }

  Future<void> _loadUserData() async {
    final storedUsername = await _authService.getUsername();
    final storedEmail = await _authService.getEmail();
    setState(() {
      username = storedUsername ?? 'User';
      email = storedEmail ?? 'user@example.com';
    });
  }

  Future<int> _getNotificationCount() async {
    final tickets = await NotificationService.getTickets();
    return tickets.length;
  }
    Future<void> fetchAdverts() async {
      try {
        print('Attempting to fetch adverts from: ${AppConfig.advertsEndpoint}');
        final response = await http.get(
          Uri.parse(AppConfig.advertsEndpoint),
        ).timeout(const Duration(seconds: 10));

        print('Response status: ${response.statusCode}');
        if (response.statusCode == 200) {
          final List<dynamic> data = json.decode(response.body);
          setState(() {
            adverts = data.map((json) => Advert.fromJson(json)).toList();
          });
          print('Loaded ${adverts.length} adverts');
        } else {
          print('Failed to load adverts: ${response.statusCode}');
          print('Response body: ${response.body}');
        }
      } catch (e) {
        print('Error fetching adverts: $e');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to connect to server: $e')),
          );
        }
      }
    }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D47A1),
        leadingWidth: 200,
        leading: Builder(
          builder: (BuildContext context) {
            return InkWell(
              onTap: () {
                Scaffold.of(context).openDrawer();
              },
              child: Row(
                children: [
                  const SizedBox(width: 10),
                  CircleAvatar(
                    radius: 18,
                    backgroundColor: Colors.white,
                    child: Text(
                      username.isNotEmpty ? username[0].toUpperCase() : 'U',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade900,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Hi, $username',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        actions: [
          FutureBuilder<int>(
            future: _getNotificationCount(),
            builder: (context, snapshot) {
              final count = snapshot.data ?? 0;
              return InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => NotificationScreen(),
                    ),
                  );
                },
                child: Stack(
                  children: [
                    const Padding(
                      padding: EdgeInsets.all(12.0),
                      child: Icon(Icons.notifications, color: Colors.white),
                    ),
                    if (count > 0)
                      Positioned(
                        right: 10,
                        top: 6,
                        child: Container(
                          padding: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            color: Colors.red,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          constraints: const BoxConstraints(
                            minWidth: 10,
                            minHeight: 10,
                          ),
                          child: Text(
                            count > 99 ? '99+' : count.toString(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 8,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      backgroundColor: Colors.white,
      drawer: _buildDrawer(),
      body: ListView.builder(
        padding: const EdgeInsets.only(bottom: 20),
        itemCount: 3 + adverts.length, // Carousel + Services + Title + dynamic adverts
        itemBuilder: (context, index) {
          if (index == 0) {
            return _buildCarousel();
          } else if (index == 1) {
            return _buildServices();
          } else if (index == 2) {
            return _buildAdvertTitle();
          } else {
            final ad = adverts[index - 3];
            return _adTile(ad.imageUrl, ad.title, ad.description, ad.linkUrl);
          }
        },
      ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          UserAccountsDrawerHeader(
            decoration: BoxDecoration(
              color: Colors.blue.shade900,
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Colors.blue.shade800, Colors.blue.shade900],
              ),
            ),
            accountName: Text(
              username,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            accountEmail: Text(
              email,
              style: TextStyle(color: Colors.white.withOpacity(0.9)),
            ),
            currentAccountPicture: GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const EditProfilePage()),
                );
              },
              child: CircleAvatar(
                backgroundColor: Colors.white,
                child: Text(
                  username.isNotEmpty ? username[0].toUpperCase() : 'U',
                  style: TextStyle(
                    fontSize: 24,
                    color: Colors.blue.shade900,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
          _drawerItem(Icons.person, 'Profile', () => Navigator.pop(context)),
          _drawerItem(Icons.book, 'My Bookings', () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const BookingsPage()),
            );
          }),
          const Divider(),
          _drawerItem(Icons.settings, 'Settings', () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const SettingsPage()),
            );
          }),
          _drawerItem(Icons.language, 'Language', () {}),
          ListTile(
            leading: const Icon(Icons.dark_mode),
            title: const Text('Dark Mode'),
            trailing: Switch(
              value: true,
              onChanged: (value) {},
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Log Out', style: TextStyle(color: Colors.red)),
            onTap: () async {
              final result = await _authService.logoutUser();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(result['message'])),
              );
              if (result['success']) {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (context) => const SignInScreen()),
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _drawerItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      onTap: onTap,
    );
  }

  Widget _buildCarousel() {
    return Column(
      children: [
        const SizedBox(height: 10),
        CarouselSlider(
          items: my_images,
          options: CarouselOptions(
            onPageChanged: (index, reason) {
              setState(() {
                _currentIndex = index;
              });
            },
            height: 200,
            autoPlay: true,
            viewportFraction: 0.9,
            enlargeCenterPage: true,
            enableInfiniteScroll: true,
            autoPlayInterval: const Duration(seconds: 4),
            autoPlayAnimationDuration: const Duration(milliseconds: 800),
            autoPlayCurve: Curves.fastOutSlowIn,
          ),
        ),
        const SizedBox(height: 10),
        AnimatedSmoothIndicator(
          activeIndex: _currentIndex,
          count: my_images.length,
          effect: ExpandingDotsEffect(
            dotHeight: 8,
            dotWidth: 8,
            activeDotColor: Colors.blue.shade900,
            dotColor: Colors.grey.shade400,
            expansionFactor: 2.0,
          ),
        ),
      ],
    );
  }

  Widget _buildServices() {
    return Column(
      children: [
        const SizedBox(height: 20),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            children: [
              Text(
                'Services',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade900),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _serviceCard(Icons.access_alarm, 'Timely Arrival',
                  Colors.amber.shade700),
              _serviceCard(Icons.directions_bus, 'Comfy Rides',
                  Colors.green.shade700),
              _serviceCard(Icons.security, 'Safe Travel', Colors.red.shade700),
            ],
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildAdvertTitle() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16.0, 8.0, 16.0, 12.0),
      child: Row(
        children: [
          Text(
            'Advertisements',
            style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade900),
          ),
        ],
      ),
    );
  }

 Widget _adTile(String imageUrl, String title, String subtitle, [String? linkUrl]) {
  return InkWell(
    onTap: linkUrl != null && linkUrl.isNotEmpty
        ? () async {
            final Uri url = Uri.parse(linkUrl);
              if (await canLaunchUrl(url)) {
                await launchUrl(url, mode: LaunchMode.platformDefault);
              } else {
                print('Could not launch $linkUrl');
              }
          }
        : null,
    child: Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                  image: DecorationImage(
                    image: NetworkImage(imageUrl),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: const TextStyle(fontSize: 13, color: Colors.grey),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const Divider(height: 1),
      ],
    ),
  );
}


  Widget _serviceCard(IconData icon, String title, Color color) {
    return Expanded(
      child: Column(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 6,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Icon(icon, size: 30, color: Colors.white),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: Colors.black87),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class ViewPage extends StatelessWidget {
  final String imagePath;
  final String title;
  final String subtitle;

  const ViewPage({
    super.key,
    required this.imagePath,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Details page'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(4.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: double.infinity,
                height: 250,
                padding: EdgeInsets.symmetric(horizontal: 5),
                child: Image.asset(imagePath, fit: BoxFit.cover),
              ),
            ),
            SizedBox(height: 20),
            Text(
              title,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              subtitle,
              style: TextStyle(fontSize: 16),
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
