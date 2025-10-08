import 'package:bus_app/edit_profile_page.dart';
import 'package:bus_app/login_screen.dart';
import 'package:bus_app/notification.dart';
import 'package:bus_app/services/auth_service.dart';
import 'package:bus_app/settings_page.dart';
import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:bus_app/bookings_page.dart'; // Import the BookingsPage

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  final AuthService _authService = AuthService();
  String username = '';

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
    _loadUsername();
  }

  Future<void> _loadUsername() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      username = prefs.getString('username') ?? '';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D47A1),
        leadingWidth:
            200, // Increased leading width to accommodate full username
        leading: Builder(
          builder: (BuildContext context) {
            return InkWell(
              onTap: () {
                Scaffold.of(context).openDrawer();
              },
              child: Row(
                children: [
                  const SizedBox(width: 10),
                  const CircleAvatar(
                    radius: 18,
                    backgroundImage: AssetImage('images/IMG_E5781.JPG'),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    // Wrap Text with Expanded to handle overflow (but now with more space)
                    child: Text(
                      'Hi, $username', // ✅ Now this will work
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                        color: Colors.white,
                      ),
                      // Removed overflow: TextOverflow.ellipsis to show full name
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        actions: [
          InkWell(
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
                // Badge
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
                    child: const Text(
                      '2', // Replace with your dynamic count
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 8,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      backgroundColor: Colors.white,
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            UserAccountsDrawerHeader(
              decoration: BoxDecoration(
                color: Colors.blue.shade900, // Matches your app bar color
                gradient: LinearGradient(
                  // Optional: Adds a nice gradient effect
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.blue.shade800,
                    Colors.blue.shade900,
                  ],
                ),
              ),
              accountName: Text(
                'Okema Paul',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              accountEmail: Text(
                'okema@gmail.com',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.9),
                ),
              ),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Colors.white, // White background for contrast
                child: GestureDetector(
                  child: Text(
                    'OP', // Using both initials
                    style: TextStyle(
                      fontSize: 24,
                      color: Colors.blue.shade900, // Matches your theme
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const EditProfilePage()),
                    );
                  },
                ),
              ),
            ),
            // Main Navigation
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16.0),
              child: Text('Navigation',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            ),
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Profile'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.book),
              title: const Text('My Bookings'),
              onTap: () {
                Navigator.pop(context); // Close the drawer
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const BookingsPage()),
                );
              },
            ),

            const Divider(),

            // App Settings
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16.0),
              child: Text('Preferences',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Settings'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const SettingsPage()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.language),
              title: const Text('Language'),
              onTap: () {}, // Language settings
            ),
            ListTile(
              leading: const Icon(Icons.dark_mode),
              title: const Text('Dark Mode'),
              trailing: Switch(
                value: true, // Replace with actual state
                onChanged: (value) {},
              ),
            ),

            const Divider(),
            // Logout

            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Log Out', style: TextStyle(color: Colors.red)),
              onTap: () async {
                final result = await _authService.logoutUser();

                if (result['success']) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(result['message'])),
                  );

                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const SignInScreen()),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(result['message'])),
                  );
                }
              },
            ),
          ],
        ),
      ),
      body: ListView.separated(
        padding:
            const EdgeInsets.only(bottom: 20), // Padding for the overall list
        itemCount: 7, // Adjust based on number of sections + separators
        separatorBuilder: (context, index) {
          // Add space between Carousel, Services, and Advertisements title
          if (index == 0) {
            return const SizedBox(height: 20);
          } else if (index == 1) {
            return const SizedBox(
                height: 30); // Increased space after Services section
          } else if (index == 2 || index == 4) {
            return const SizedBox(height: 20);
          }
          return const SizedBox.shrink(); // No separator for other items
        },
        itemBuilder: (context, index) {
          if (index == 0) {
            // Carousel Slider section
            return Column(
              children: [
                const SizedBox(height: 10), // Reduced spacing at the top
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
                    autoPlayAnimationDuration:
                        const Duration(milliseconds: 800),
                    autoPlayCurve: Curves.fastOutSlowIn,
                  ),
                ),
                const SizedBox(height: 10), // Reduced spacing
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
          } else if (index == 1) {
            // Services Section
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.start,
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
                const SizedBox(height: 10), // Reduced spacing
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _serviceCard(Icons.access_alarm, 'Timely Arrival',
                          Colors.amber.shade700),
                      _serviceCard(Icons.directions_bus, 'Comfy Rides',
                          Colors.green.shade700),
                      _serviceCard(
                          Icons.security, 'Safe Travel', Colors.red.shade700),
                    ],
                  ),
                ),
              ],
            );
          } else if (index == 2) {
            // Advertisements Title
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
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
          } else if (index == 3) {
            // First Advertisement
            return _adTile('images/hotel.jpg', 'Khemi Hotel',
                'Your number one hotel in town with the best services, offering luxurious stays and exquisite dining.');
          } else if (index == 4) {
            // Second Advertisement
            return _adTile('images/concert.jpg', 'Live Concert',
                'Experience the best music live from top artists, a night to remember with friends and family.');
          } else if (index == 5) {
            // Third Advertisement
            return _adTile('images/4.jpg', 'Travel Insurance',
                'Get insured for a safe journey, protecting you from unforeseen events and travel disruptions.');
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }

  Widget _adTile(String imagePath, String title, String subtitle) {
    return Column(
      // Direct Column structure, removed Padding
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0), // Added padding for individual list items
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                  image: DecorationImage(
                    image: AssetImage(imagePath),
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
                          color: Colors.blue.shade800),
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
        const Divider(height: 1), // Add a divider below each ad tile
      ],
    );
  }

  Widget _serviceCard(IconData icon, String title, Color color) {
    return Expanded(
      child: Column(
        // Replaced Card with Column
        children: [
          Container(
            width: 60, // Icon container size remains
            height: 60, // Icon container size remains
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
          const SizedBox(height: 8), // Adjusted spacing
          Text(
            title,
            textAlign:
                TextAlign.center, // Keep center alignment for consistency
            style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: Colors.black87), // Font size remains
            maxLines: 1, // Ensure single line
            overflow: TextOverflow.ellipsis, // Add ellipsis if overflow
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
