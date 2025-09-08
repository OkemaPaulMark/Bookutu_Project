import 'package:flutter/material.dart';
import 'seats_page.dart';

class BusListScreen extends StatefulWidget {
  BusListScreen({super.key});

  @override
  State<BusListScreen> createState() => _BusListScreenState();
}

class _BusListScreenState extends State<BusListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchText = '';

  final List<String> ugandanDistricts = [
    'Kampala',
    'Wakiso',
    'Mukono',
    'Jinja',
    'Mbarara',
    'Gulu',
    'Fort Portal',
    'Masaka',
    'Mbale',
    'Arua',
    'Soroti',
    'Lira',
    'Hoima',
    'Entebbe',
    'Kabale',
    'Tororo',
  ];

  final Map<String, List<Map<String, String>>> busCompanies = {
    'Global Coaches': [
      {
        'from': 'Kampala',
        'to': 'Mbarara',
        'image': 'images/1.jpg',
        'seats': '25',
        'departure': '6:00 AM',
      },
      {
        'from': 'Mbarara',
        'to': 'Kampala',
        'image': 'images/bus.jpg',
        'seats': '30',
        'departure': '9:00 AM',
      },
      {
        'from': 'Kampala',
        'to': 'Gulu',
        'image': 'images/2.jpg',
        'seats': '28',
        'departure': '1:00 PM',
      },
      {
        'from': 'Jinja',
        'to': 'Mbarara',
        'image': 'images/1.jpg',
        'seats': '20',
        'departure': '3:00 PM',
      },
    ],
    'YY Coaches': [
      {
        'from': 'Jinja',
        'to': 'Kampala',
        'image': 'images/2.jpg',
        'seats': '20',
        'departure': '7:00 AM',
      },
      {
        'from': 'Kampala',
        'to': 'Gulu',
        'image': 'images/1.jpg',
        'seats': '28',
        'departure': '10:30 AM',
      },
      {
        'from': 'Mbarara',
        'to': 'Jinja',
        'image': 'images/bus.jpg',
        'seats': '18',
        'departure': '2:00 PM',
      },
      {
        'from': 'Gulu',
        'to': 'Kampala',
        'image': 'images/2.jpg',
        'seats': '32',
        'departure': '4:00 PM',
      },
    ],
    'Friendship': [
      {
        'from': 'Masaka',
        'to': 'Kampala',
        'image': 'images/bus.jpg',
        'seats': '22',
        'departure': '8:00 AM',
      },
      {
        'from': 'Kampala',
        'to': 'Mbale',
        'image': 'images/2.jpg',
        'seats': '35',
        'departure': '11:00 AM',
      },
      {
        'from': 'Mbale',
        'to': 'Masaka',
        'image': 'images/1.jpg',
        'seats': '24',
        'departure': '1:30 PM',
      },
      {
        'from': 'Kampala',
        'to': 'Hoima',
        'image': 'images/bus.jpg',
        'seats': '26',
        'departure': '5:00 PM',
      },
    ],
  };

  List<Map<String, String>> get filteredBuses {
    if (_searchText.isEmpty) {
      // When no search, we don't need companyName in the individual bus map here
      return busCompanies.values.expand((element) => element).toList();
    } else {
      List<Map<String, String>> searchResults = [];
      busCompanies.forEach((companyName, buses) {
        for (var bus in buses) {
          if (bus['from']!.toLowerCase().contains(_searchText.toLowerCase()) ||
              bus['to']!.toLowerCase().contains(_searchText.toLowerCase())) {
            searchResults.add({
              ...bus,
              'companyName': companyName, // Add company name to the bus data
            });
          }
        }
      });
      return searchResults;
    }
  }

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchText = _searchController.text;
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus List', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60.0),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by location...',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide.none,
                ),
                prefixIcon: const Icon(Icons.search),
              ),
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.only(bottom: 80),
          children: [
            if (_searchText.isEmpty)
              ...busCompanies.entries.map((entry) {
                final String companyName = entry.key;
                final List<Map<String, String>> companyBuses = entry.value;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    buildSectionHeader(
                        companyName, ""), // Company Name as header
                    buildTwoColumnCardSection(companyBuses, context),
                    const SizedBox(height: 20),
                  ],
                );
              }).toList()
            else if (filteredBuses.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  buildSectionHeader("Search Results", ""),
                  buildTwoColumnCardSection(filteredBuses, context),
                  const SizedBox(height: 20),
                ],
              )
            else
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text("No buses found for your search.",
                    style: TextStyle(fontSize: 16)),
              ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text("Feature coming soon!",
                    style: TextStyle(color: Colors.white))),
          );
        },
        backgroundColor: Colors.blue.shade900,
        label:
            const Text("Book for later", style: TextStyle(color: Colors.white)),
        icon: const Icon(Icons.schedule, color: Colors.white),
      ),
    );
  }

  Widget buildSectionHeader(String title, String date) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title,
              style:
                  const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Row(
            children: [
              if (date.isNotEmpty) // Only show date if it's not empty
                Text(date,
                    style: const TextStyle(fontSize: 14, color: Colors.grey)),
              if (title != "Search Results" &&
                  date.isEmpty) // Show "View All" only for company sections
                TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ViewAllBusesScreen(
                          companyName: title,
                          buses: busCompanies[title]!,
                        ),
                      ),
                    );
                  },
                  child: const Text("View All",
                      style: TextStyle(color: Colors.blue, fontSize: 14)),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildTwoColumnCardSection(
      List<Map<String, String>> data, BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: SizedBox(
        height: 400, // Increased height for the cards to prevent overflow
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          itemCount: data.length,
          itemBuilder: (context, index) {
            final item = data[index];
            final String? companyName =
                item['companyName']; // Extract companyName if present
            return Padding(
              padding:
                  const EdgeInsets.only(right: 12.0), // Spacing between cards
              child: SizedBox(
                width: MediaQuery.of(context).size.width / 2 -
                    22, // Two cards visible at once with padding
                height: 400, // Explicitly set height for individual cards
                child: BusCard(
                    item: item,
                    context: context,
                    companyName: companyName), // Pass companyName
              ),
            );
          },
        ),
      ),
    );
  }

  Widget buildCard(Map<String, String> item, BuildContext context) {
    // This method is no longer directly used for building cards in the main view
    // as BusCard is used directly in ListView.builder.
    // It's kept for the ViewAllBusesScreen if needed or can be removed if not.
    return BusCard(item: item, context: context);
  }
}

class ViewAllBusesScreen extends StatelessWidget {
  final String companyName;
  final List<Map<String, String>> buses;

  const ViewAllBusesScreen(
      {super.key, required this.companyName, required this.buses});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('$companyName Buses',
            style: const TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        iconTheme: const IconThemeData(
            color: Colors.white), // Set back button color to white
      ),
      body: SafeArea(
        child: GridView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: buses.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 0.5, // Adjusted aspect ratio for taller cards
          ),
          itemBuilder: (context, index) {
            final item = buses[index];
            return BusCard(
                item: item,
                context: context,
                companyName: companyName); // Pass companyName to BusCard
          },
        ),
      ),
    );
  }
}

// Extracted BusCard widget for reusability
class BusCard extends StatelessWidget {
  final Map<String, String> item;
  final BuildContext context;
  final String? companyName; // Added companyName

  const BusCard(
      {super.key, required this.item, required this.context, this.companyName});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Image.asset(
              item['image']!,
              width: double.infinity,
              height: 100, // Image height remains 100
              fit: BoxFit.cover,
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (companyName != null)
                    Text(companyName!,
                        style:
                            const TextStyle(fontSize: 12, color: Colors.grey)),
                  if (companyName != null) const SizedBox(height: 2),
                  Text("From: ${item['from']}",
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 2),
                  Text("To: ${item['to']}"),
                  const SizedBox(height: 2),
                  Text("Departure: ${item['departure']}"),
                  Text("Seats: ${item['seats']}"),
                  const Spacer(), // Pushes the button to the bottom
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                SeatSelectionScreen(busData: {}),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade900,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        minimumSize: const Size(0, 36), // Ensures it fits well
                      ),
                      child: const Text(
                        "Book Now",
                        style: TextStyle(color: Colors.white, fontSize: 14),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
