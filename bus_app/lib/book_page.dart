import 'package:flutter/material.dart';
import 'seats_page.dart';

class BusListScreen extends StatelessWidget {
  BusListScreen({super.key});

  final List<Map<String, String>> movingTodayKampalaToJuba = [
    {
      'from': 'Kampala',
      'to': 'Juba',
      'image': 'images/1.jpg',
      'seats': '14',
      'departure': '6:30 AM',
    },
    {
      'from': 'Kampala',
      'to': 'Juba',
      'image': 'images/bus.jpg',
      'seats': '20',
      'departure': '9:00 AM',
    },
  ];

  final List<Map<String, String>> movingTodayJubaToKampala = [
    {
      'from': 'Juba',
      'to': 'Kampala',
      'image': 'images/bus.jpg',
      'seats': '12',
      'departure': '7:45 AM',
    },
    {
     'from': 'Juba',
      'to': 'Kampala',
      'image': 'images/1.jpg',
      'seats': '16',
      'departure': '10:00 AM',
    },
  ];

  final List<Map<String, String>> movingTomorrowKampalaToJuba = [
    {
      'from': 'Kampala',
      'to': 'Juba',
      'image': 'images/2.jpg',
      'seats': '14',
      'departure': '6:30 AM',
    },
    {
      'from': 'Kampala',
      'to': 'Juba',
      'image': 'images/1.jpg',
      'seats': '18',
      'departure': '9:30 AM',
    },
  ];

  final List<Map<String, String>> movingTomorrowJubaToKampala = [
    {
      'from': 'Juba',
      'to': 'Kampala',
      'image': 'images/1.jpg',
      'seats': '12',
      'departure': '7:45 AM',
    },
    {
      'from': 'Juba',
      'to': 'Kampala',
      'image': 'images/bus.jpg',
      'seats': '20',
      'departure': '10:00 AM',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus List', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.only(bottom: 80),
          children: [
            buildSectionHeader("Moving Today", "07/05/2025"),
            buildSubText("From Kampala to Juba"),
            buildTwoColumnCardSection(movingTodayKampalaToJuba, context),
            buildSubText("From Juba to Kampala"),
            buildTwoColumnCardSection(movingTodayJubaToKampala, context),
            const SizedBox(height: 20),
            buildSectionHeader("Moving Tomorrow", "08/05/2025"),
            buildSubText("From Kampala to Juba"),
            buildTwoColumnCardSection(movingTomorrowKampalaToJuba, context),
            buildSubText("From Juba to Kampala"),
            buildTwoColumnCardSection(movingTomorrowJubaToKampala, context),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Feature coming soon!", style: TextStyle(color: Colors.white))),
          );
        },
        backgroundColor: Colors.blue.shade900,
        label: const Text("Book for later", style: TextStyle(color: Colors.white)),
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
          Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text(date, style: const TextStyle(fontSize: 14, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget buildSubText(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Text(
        text,
        style: const TextStyle(fontSize: 14, color: Colors.black54),
      ),
    );
  }

  Widget buildTwoColumnCardSection(List<Map<String, String>> data, BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: LayoutBuilder(
        builder: (context, constraints) {
          return GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: data.length,
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 3 / 4,
            ),
            itemBuilder: (context, index) {
              final item = data[index];
              return buildCard(item, context);
            },
          );
        },
      ),
    );
  }

  Widget buildCard(Map<String, String> item, BuildContext context) {
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
            height: 66,
            fit: BoxFit.cover,
          ),
        ),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("From: ${item['from']}", style: const TextStyle(fontWeight: FontWeight.bold)),
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
                          builder: (context) => SeatSelectionScreen(busData: {}),
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
