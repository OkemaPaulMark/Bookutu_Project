import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:qr_flutter/qr_flutter.dart';
import 'services/auth_service.dart';
import 'services/notification_service.dart';
import '../config/app_config.dart';

class TicketScreen extends StatefulWidget {
  final Map<String, dynamic> bookingData;
  final Map<String, String> tripData;
  final bool isPreview;
  final bool viewOnly;

  const TicketScreen({super.key, required this.bookingData, required this.tripData, this.isPreview = false, this.viewOnly = false});

  @override
  State<TicketScreen> createState() => _TicketScreenState();
}

class _TicketScreenState extends State<TicketScreen> {
  bool isBookingConfirmed = false;
  bool isLoading = false;
  Map<String, dynamic>? confirmedBookingData;
  final GlobalKey _ticketKey = GlobalKey();

  String _generateTicketId() {
    if (isBookingConfirmed && confirmedBookingData != null) {
      return confirmedBookingData!['booking_reference'] ?? 'TKT-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}';
    }
    return 'TKT-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}';
  }

  Future<void> _confirmBooking() async {
    setState(() {
      isLoading = true;
    });

    try {
      final authService = AuthService();
      final token = await authService.getAccessToken();
      
      final response = await http.post(
        Uri.parse(AppConfig.bookingsEndpoint),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'trip_id': int.parse(widget.tripData['id']!),
          'seat_numbers': widget.bookingData['seat_numbers'],
          'passenger_name': widget.bookingData['passenger_name'],
          'passenger_phone': '0700000000',
        }),
      );

      if (response.statusCode == 200) {
        final bookingData = json.decode(response.body);
        setState(() {
          confirmedBookingData = bookingData;
          isBookingConfirmed = true;
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Booking confirmed successfully!')),
        );
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error['error'] ?? 'Booking failed')),
        );
        setState(() {
          isLoading = false;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error confirming booking: $e')),
      );
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Your Ticket', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Ticket Details Card
            RepaintBoundary(
              key: _ticketKey,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.shade300,
                      blurRadius: 10,
                      spreadRadius: 2,
                    )
                  ],
                ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // QR Code at top
                  QrImageView(
                    data: (confirmedBookingData ?? widget.bookingData)['booking_reference'] ?? 'PREVIEW',
                    version: QrVersions.auto,
                    size: 120.0,
                    backgroundColor: Colors.white,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    "BUS TICKET",
                    style: TextStyle(
                        fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  // Ticket info rows
                  buildRow("Ticket ID", _generateTicketId()),
                  buildRow("Passenger", widget.bookingData['passenger_name'] ?? 'N/A'),
                  buildRow("Date", widget.tripData['departure_date'] ?? DateTime.now().toString().split(' ')[0]),
                  buildRow("Seat Numbers", (widget.bookingData['seat_numbers'] as List).join(', ')),
                  const Divider(),
                  buildRow("Route", widget.tripData['route_name'] ?? 'N/A'),
                  buildRow("Bus Company", widget.tripData['company_name'] ?? 'N/A'),
                  buildRow("Number Plate", widget.tripData['bus_registration'] ?? 'N/A'),
                  const Divider(),
                  buildRow("Departure Time", widget.tripData['departure_time'] ?? 'N/A'),
                  if (!widget.isPreview || isBookingConfirmed)
                    buildRow("Status", (confirmedBookingData ?? widget.bookingData)['status'] ?? 'N/A'),
                  const Divider(),
                  buildRow("Total Amount", 'UGX ${widget.bookingData['total_amount']?.toStringAsFixed(0) ?? '0'}'),
                ],
              ),
            ),
            ),

            const SizedBox(height: 30),

            // Action Button
            if (!widget.viewOnly)
              if (widget.isPreview && !isBookingConfirmed)
                ElevatedButton(
                  onPressed: isLoading ? null : _confirmBooking,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    minimumSize: const Size.fromHeight(50),
                  ),
                  child: isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          "Confirm Booking",
                          style: TextStyle(fontSize: 16, color: Colors.white),
                        ),
                )
              else if (isBookingConfirmed || !widget.isPreview)
                ElevatedButton.icon(
                  onPressed: _saveToNotifications,
                  icon: const Icon(Icons.notifications, color: Colors.white),
                  label: const Text(
                    "Save to Notifications",
                    style: TextStyle(fontSize: 16, color: Colors.white),
                  ),
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

  Future<void> _saveToNotifications() async {
    try {
      await NotificationService.saveTicket(
        bookingData: confirmedBookingData ?? widget.bookingData,
        tripData: widget.tripData,
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Ticket saved to notifications! Check the notifications page.'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving ticket: $e')),
      );
    }
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

  Widget buildPaymentCard(String imagePath, String label) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 6,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Image.asset(imagePath, height: 40),
          const SizedBox(height: 10),
          Text(
            label,
            style:
                const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
