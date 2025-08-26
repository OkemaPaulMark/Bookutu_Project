import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

class TicketScreen extends StatelessWidget {
  final Map<String, String> ticketDetails = {
    'passengerName': 'John Doe',
    'seatNumber': 'A12',
    'numberPlate': 'UBX 123A',
    'departure': 'Juba',
    'destination': 'Kampala',
    'departureTime': '08:00 AM',
    'arrivalTime': '06:00 PM',
    'date': '10th Feb 2025',
    'ticketID': 'TKT-987654',
    'price': '\$25.00'
  };

  TicketScreen({super.key});

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
            Container(
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
                    data: ticketDetails['ticketID']!,
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
                  buildRow("Passenger", ticketDetails['passengerName']!),
                  buildRow("Seat Number", ticketDetails['seatNumber']!),
                  const Divider(),
                  buildRow("Bus Number", ticketDetails['numberPlate']!),
                  buildRow("Departure", ticketDetails['departure']!),
                  buildRow("Destination", ticketDetails['destination']!),
                  const Divider(),
                  buildRow("Departure Time", ticketDetails['departureTime']!),
                  buildRow("Arrival Time", ticketDetails['arrivalTime']!),
                  buildRow("Date", ticketDetails['date']!),
                  const Divider(),
                  buildRow("Ticket ID", ticketDetails['ticketID']!),
                  buildRow("Price", ticketDetails['price']!),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Payment Options (Grid Cards)
            Container(
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
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Select payment method",
                    style:
                        TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const Divider(height: 24),
                  const SizedBox(height: 16),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 3 / 2,
                    children: [
                      buildPaymentCard("images/mtn.png", "MTN Momo"),
                      buildPaymentCard("images/airtel.jpg", "Airtel Money"),
                      buildPaymentCard("images/visa.png", "Visa"),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),

            // Download Button
            ElevatedButton.icon(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Download started...')),
                );
              },
              icon: const Icon(
                Icons.download,
                color: Colors.white,
              ),
              label: const Text(
                "Download Your Ticket",
                style: TextStyle(fontSize: 16, color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue.shade900,
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                textStyle: const TextStyle(fontSize: 16),
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
