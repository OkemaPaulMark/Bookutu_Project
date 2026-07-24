import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:provider/provider.dart';

import '../controllers/auth_controller.dart';
import '../controllers/home_controller.dart';
import '../widgets/advert_tile.dart';
import '../widgets/service_card.dart';
import 'sign_in_view.dart';
import 'bookings_view.dart';
import 'notification_view.dart';
import 'edit_profile_view.dart';
import 'settings_view.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<HomeController>(
      create: (_) => HomeController(),
      child: const _HomeView(),
    );
  }
}

class _HomeView extends StatefulWidget {
  const _HomeView();

  @override
  State<_HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<_HomeView> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadAdverts());
  }

  Future<void> _loadAdverts() async {
    final controller = context.read<HomeController>();
    await controller.loadAdverts();
    if (!mounted) return;
    if (controller.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(controller.errorMessage!)),
      );
    }
  }

  final List<Widget> _carouselImages = [
    Container(
      margin: const EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: const DecorationImage(image: AssetImage('images/bus1.jpg'), fit: BoxFit.cover),
      ),
    ),
    Container(
      margin: const EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: const DecorationImage(image: AssetImage('images/bus2.jpg'), fit: BoxFit.cover),
      ),
    ),
    Container(
      margin: const EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: const DecorationImage(image: AssetImage('images/bus3.jpeg'), fit: BoxFit.cover),
      ),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final authController = context.watch<AuthController>();
    final homeController = context.watch<HomeController>();
    final username = authController.username;
    final email = authController.email;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D47A1),
        leadingWidth: 200,
        leading: Builder(
          builder: (context) {
            return InkWell(
              onTap: () => Scaffold.of(context).openDrawer(),
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
            future: homeController.getNotificationCount(),
            builder: (context, snapshot) {
              final count = snapshot.data ?? 0;
              return InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const NotificationScreen()),
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
                          constraints: const BoxConstraints(minWidth: 10, minHeight: 10),
                          child: Text(
                            count > 99 ? '99+' : count.toString(),
                            style: const TextStyle(color: Colors.white, fontSize: 8),
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
      drawer: _buildDrawer(context, username, email, authController),
      body: ListView.builder(
        padding: const EdgeInsets.only(bottom: 20),
        itemCount: 3 + _advertItemCount(homeController),
        itemBuilder: (context, index) {
          if (index == 0) return _buildCarousel();
          if (index == 1) return _buildServices();
          if (index == 2) return _buildAdvertTitle();
          if (homeController.adverts.isEmpty) return _buildNoAdvertsMessage();
          return AdvertTile(advert: homeController.adverts[index - 3]);
        },
      ),
    );
  }

  int _advertItemCount(HomeController controller) {
    if (controller.isLoading) return 0;
    return controller.adverts.isEmpty ? 1 : controller.adverts.length;
  }

  Widget _buildNoAdvertsMessage() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 24.0),
      child: Center(
        child: Text(
          'No adverts available yet',
          style: TextStyle(fontSize: 14, color: Colors.grey),
        ),
      ),
    );
  }

  Widget _buildDrawer(
    BuildContext context,
    String username,
    String email,
    AuthController authController,
  ) {
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
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            accountEmail: Text(email, style: TextStyle(color: Colors.white.withValues(alpha: 0.9))),
            currentAccountPicture: GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const EditProfilePage()),
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
            trailing: Switch(value: true, onChanged: (value) {}),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Log Out', style: TextStyle(color: Colors.red)),
            onTap: () async {
              await authController.logout();
              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Logged out successfully from device.')),
              );
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const SignInScreen()),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _drawerItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(leading: Icon(icon), title: Text(title), onTap: onTap);
  }

  Widget _buildCarousel() {
    return Column(
      children: [
        const SizedBox(height: 10),
        CarouselSlider(
          items: _carouselImages,
          options: CarouselOptions(
            onPageChanged: (index, reason) {
              setState(() => _currentIndex = index);
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
          count: _carouselImages.length,
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
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue.shade900),
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
              ServiceCard(icon: Icons.access_alarm, title: 'Timely Arrival', color: Colors.amber.shade700),
              ServiceCard(icon: Icons.directions_bus, title: 'Comfy Rides', color: Colors.green.shade700),
              ServiceCard(icon: Icons.security, title: 'Safe Travel', color: Colors.red.shade700),
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
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue.shade900),
          ),
        ],
      ),
    );
  }
}
