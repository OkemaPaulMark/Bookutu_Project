import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../controllers/ticket_controller.dart';
import '../models/booking.dart';
import '../models/trip.dart';

class TicketScreen extends StatelessWidget {
  final Trip trip;
  final Booking booking;
  final bool isPreview;
  final bool viewOnly;

  const TicketScreen({
    super.key,
    required this.trip,
    required this.booking,
    this.isPreview = false,
    this.viewOnly = false,
  });

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<TicketController>(
      create: (_) => TicketController(),
      child: _TicketView(
        trip: trip,
        preview: booking,
        isPreview: isPreview,
        viewOnly: viewOnly,
      ),
    );
  }
}

class _TicketView extends StatelessWidget {
  final Trip trip;
  final Booking preview;
  final bool isPreview;
  final bool viewOnly;

  const _TicketView({
    required this.trip,
    required this.preview,
    required this.isPreview,
    required this.viewOnly,
  });

  Future<void> _confirmBooking(BuildContext context, TicketController controller) async {
    final success = await controller.confirmBooking(trip: trip, preview: preview);
    if (!context.mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Booking confirmed successfully!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(controller.errorMessage ?? 'Booking failed')),
      );
    }
  }

  Future<void> _saveToNotifications(BuildContext context, TicketController controller) async {
    try {
      await controller.saveToNotifications(preview: preview, trip: trip);
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Ticket saved to notifications! Check the notifications page.'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving ticket: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<TicketController>();
    final displayed = controller.confirmedBooking ?? preview;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Ticket', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.grey.shade300, blurRadius: 10, spreadRadius: 2),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  QrImageView(
                    data: displayed.bookingReference ?? 'PREVIEW',
                    version: QrVersions.auto,
                    size: 120.0,
                    backgroundColor: Colors.white,
                  ),
                  const SizedBox(height: 12),
                  const Text("BUS TICKET", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  buildRow("Ticket ID", controller.ticketId(preview)),
                  buildRow("Passenger", preview.passengerName),
                  buildRow("Date", trip.departureDate),
                  buildRow("Seat Numbers", preview.seatNumbers.join(', ')),
                  const Divider(),
                  buildRow("Route", trip.routeName),
                  buildRow("Bus Company", trip.companyName),
                  buildRow("Number Plate", trip.busRegistration),
                  const Divider(),
                  buildRow("Departure Time", trip.departureTime),
                  if (!isPreview || controller.isBookingConfirmed) buildRow("Status", displayed.status),
                  const Divider(),
                  buildRow("Total Amount", 'UGX ${preview.totalAmount.toStringAsFixed(0)}'),
                ],
              ),
            ),
            const SizedBox(height: 30),
            if (!viewOnly)
              if (isPreview && !controller.isBookingConfirmed)
                ElevatedButton(
                  onPressed: controller.isLoading ? null : () => _confirmBooking(context, controller),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    minimumSize: const Size.fromHeight(50),
                  ),
                  child: controller.isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text("Confirm Booking", style: TextStyle(fontSize: 16, color: Colors.white)),
                )
              else if (controller.isBookingConfirmed || !isPreview)
                ElevatedButton.icon(
                  onPressed: () => _saveToNotifications(context, controller),
                  icon: const Icon(Icons.notifications, color: Colors.white),
                  label: const Text("Save to Notifications", style: TextStyle(fontSize: 16, color: Colors.white)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade900,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    minimumSize: const Size.fromHeight(50),
                  ),
                ),
          ],
        ),
      ),
    );
  }

  Widget buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(value),
        ],
      ),
    );
  }
}
