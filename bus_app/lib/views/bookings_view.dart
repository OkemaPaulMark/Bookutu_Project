import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/bookings_controller.dart';
import '../utils/company_branding.dart';

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

  Color _statusColor(String status) {
    switch (status) {
      case 'CONFIRMED':
        return Colors.green;
      case 'COMPLETED':
        return Colors.blue;
      case 'CANCELLED':
        return Colors.red;
      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<BookingsController>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Bookings', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: RefreshIndicator(
        onRefresh: controller.loadBookings,
        child: Builder(
          builder: (context) {
            if (controller.isLoading) {
              return const Center(child: CircularProgressIndicator());
            }

            if (controller.errorMessage != null) {
              return ListView(
                children: [
                  const SizedBox(height: 80),
                  Icon(Icons.error_outline, size: 48, color: Colors.red.shade300),
                  const SizedBox(height: 12),
                  Center(
                    child: Text(controller.errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
                  ),
                ],
              );
            }

            if (controller.bookings.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 80),
                  Center(
                    child: Text('No bookings found.', style: TextStyle(fontSize: 16, color: Colors.grey)),
                  ),
                ],
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: controller.bookings.length,
              itemBuilder: (context, index) {
                final booking = controller.bookings[index];
                final brandColor = CompanyBranding.colorFor(booking.companyName);
                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  elevation: 4,
                  clipBehavior: Clip.antiAlias,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: IntrinsicHeight(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Container(width: 6, color: brandColor),
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        booking.companyName,
                                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: brandColor),
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: _statusColor(booking.status).withValues(alpha: 0.15),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Text(
                                        booking.status,
                                        style: TextStyle(color: _statusColor(booking.status), fontWeight: FontWeight.bold, fontSize: 12),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text('Route: ${booking.originCity} to ${booking.destinationCity}'),
                                Text('Date: ${booking.departureDate} at ${booking.departureTime}'),
                                Text('Bus: ${booking.busRegistration}'),
                                Text('Seat: ${booking.seatLabel}'),
                                if (booking.bookingReference != null) Text('Ref: ${booking.bookingReference}'),
                                Text('Amount: UGX ${booking.totalAmount.toStringAsFixed(0)}'),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
