import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/bookings_controller.dart';

class BookingsPage extends StatelessWidget {
  const BookingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<BookingsController>(
      create: (_) => BookingsController(),
      child: const _BookingsView(),
    );
  }
}

class _BookingsView extends StatelessWidget {
  const _BookingsView();

  @override
  Widget build(BuildContext context) {
    final pastBookings = context.watch<BookingsController>().pastBookings;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Bookings', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: pastBookings.isEmpty
          ? const Center(
              child: Text('No past bookings found.', style: TextStyle(fontSize: 16, color: Colors.grey)),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: pastBookings.length,
              itemBuilder: (context, index) {
                final booking = pastBookings[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          booking.company,
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text('Route: ${booking.from} to ${booking.to}'),
                        Text('Date: ${booking.date} at ${booking.time}'),
                        Text('Seats: ${booking.seats}'),
                        Text('Status: ${booking.status}'),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
