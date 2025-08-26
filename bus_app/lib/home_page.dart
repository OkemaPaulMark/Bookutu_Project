import 'package:bus_app/login_screen.dart';
import 'package:bus_app/notification.dart';
import 'package:bus_app/services/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';

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
        leadingWidth: 130,
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
                  Text(
                    'Hi, $username', // ✅ Now this will work
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
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
              gradient: LinearGradient( // Optional: Adds a nice gradient effect
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
              child: Text(
                'OP', // Using both initials
                style: TextStyle(
                  fontSize: 24,
                  color: Colors.blue.shade900, // Matches your theme
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
            // Main Navigation
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 16.0),
        child: Text('Navigation', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      ),
      ListTile(
        leading: const Icon(Icons.person),
        title: const Text('Profile'),
        onTap: () => Navigator.pop(context),
      ),
      ListTile(
        leading: const Icon(Icons.book),
        title: const Text('My Bookings'),
        onTap: () {}, // Implement navigation
      ),
      ListTile(
        leading: const Icon(Icons.payment),
        title: const Text('Payment Methods'),
        onTap: () {}, // Implement navigation
      ),

      const Divider(),

      // App Settings
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 16.0),
        child: Text('Preferences', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      ),
      ListTile(
        leading: const Icon(Icons.settings),
        title: const Text('Settings'),
        onTap: () => Navigator.pop(context),
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
                MaterialPageRoute(builder: (context) => const SignInScreen()),
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
      body: SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(height: 5),
            CarouselSlider(
              items: my_images,
              options: CarouselOptions(
                onPageChanged: (index, reason) {
                  setState(() {
                    _currentIndex = index;
                  });
                },
                height: 180,
                autoPlay: true,
                viewportFraction: 0.8,
                enableInfiniteScroll: true,
              ),
            ),
            SizedBox(height: 10),
            AnimatedSmoothIndicator(
              activeIndex: _currentIndex,
              count: my_images.length,
              effect: WormEffect(
                dotHeight: 8,
                dotWidth: 8,
                activeDotColor: Colors.blue.shade900,
              ),
            ),
            SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Text(
                    'Services',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            SizedBox(height: 5),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _serviceCard(Icons.access_alarm, 'On-Time Arrival'),
                  _serviceCard(Icons.directions_bus, 'Comfy Rides'),
                  _serviceCard(Icons.security, 'Safe Travel'),
                ],
              ),
            ),
            SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Text(
                    'Advertisements',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            SizedBox(height: 10),
            _adTile('images/hotel.jpg'),
            _adTile('images/concert.jpg'),
            _adTile('images/4.jpg'),
            SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _adTile(String imagePath) {
    return ListTile(
      leading: Container(
        width: 60,
        height: 60,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(8),
          image: DecorationImage(
            image: AssetImage(imagePath),
            fit: BoxFit.cover,
          ),
        ),
      ),
      title: Text('Khemi Hotel'),
      subtitle: Text('Your number one hotel in town with the best services'),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ViewPage(
              imagePath: imagePath,
              title: 'Title here',
              subtitle: 'Enter subtitle here with more details...',
            ),
          ),
        );
      },
    );
  }

  Widget _serviceCard(IconData icon, String title) {
    return Column(
      children: [
        Container(
          width: 90,
          height: 90,
          decoration: BoxDecoration(
            color: Colors.blue.shade900,
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 35, color: Colors.white),
        ),
        SizedBox(height: 8),
        Text(
          title,
          textAlign: TextAlign.center,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
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
