import 'package:flutter/material.dart';

class BookingsPage extends StatelessWidget {
  const BookingsPage({super.key});

  final List<Map<String, String>> pastBookings = const [
    {
      'company': 'Global Coaches',
      'from': 'Kampala',
      'to': 'Mbarara',
      'date': '2023-10-26',
      'time': '06:00 AM',
      'seats': 'A1, A2',
      'status': 'Completed',
    },
    {
      'company': 'YY Coaches',
      'from': 'Jinja',
      'to': 'Kampala',
      'date': '2023-09-15',
      'time': '07:00 AM',
      'seats': 'B5',
      'status': 'Completed',
    },
    {
      'company': 'Friendship',
      'from': 'Masaka',
      'to': 'Kampala',
      'date': '2023-08-01',
      'time': '08:00 AM',
      'seats': 'C3, C4, C5',
      'status': 'Completed',
    },
    {
      'company': 'Global Coaches',
      'from': 'Gulu',
      'to': 'Kampala',
      'date': '2023-07-20',
      'time': '01:00 PM',
      'seats': 'D10',
      'status': 'Completed',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Bookings', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: pastBookings.isEmpty
          ? const Center(
              child: Text('No past bookings found.',
                  style: TextStyle(fontSize: 16, color: Colors.grey)),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: pastBookings.length,
              itemBuilder: (context, index) {
                final booking = pastBookings[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          booking['company']!,
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text('Route: ${booking['from']} to ${booking['to']}'),
                        Text('Date: ${booking['date']} at ${booking['time']}'),
                        Text('Seats: ${booking['seats']}'),
                        Text('Status: ${booking['status']}'),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
