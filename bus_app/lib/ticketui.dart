import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:qr_flutter/qr_flutter.dart';

import 'book_page.dart' show formatDate, formatTime, ugx;
import 'services/api_service.dart';

/// Shows one or more bookings (one per seat) as tickets, and lets the
/// passenger pay for any that are still pending.
class TicketScreen extends StatefulWidget {
  final List<dynamic> bookings;
  const TicketScreen({super.key, required this.bookings});

  @override
  State<TicketScreen> createState() => _TicketScreenState();
}

class _TicketScreenState extends State<TicketScreen> {
  late List<Map<String, dynamic>> bookings =
      widget.bookings.cast<Map<String, dynamic>>();
  String method = 'MTN';
  final phoneCtrl = TextEditingController();
  bool paying = false;

  List<Map<String, dynamic>> get pending =>
      bookings.where((b) => b['status'] == 'PENDING').toList();

  double get pendingTotal => pending.fold(
      0.0, (s, b) => s + (double.tryParse(b['total_amount'].toString()) ?? 0));

  @override
  void initState() {
    super.initState();
    phoneCtrl.text = (bookings.first['passenger_phone'] ?? '').toString();
  }

  @override
  void dispose() {
    phoneCtrl.dispose();
    super.dispose();
  }

  Future<void> _pay() async {
    if (method != 'CARD' && phoneCtrl.text.trim().length < 9) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Enter the mobile money number to charge')));
      return;
    }
    setState(() => paying = true);
    try {
      final updated = await ApiService.pay(
          pending.map<int>((b) => b['id'] as int).toList(), method, phoneCtrl.text.trim());
      final byId = {for (final b in updated) b['id']: b};
      setState(() {
        bookings = bookings.map((b) => (byId[b['id']] ?? b) as Map<String, dynamic>).toList();
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          backgroundColor: Colors.green,
          content: Text('Payment received. Your ticket is confirmed!')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => paying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.pageBg,
      appBar: AppBar(
        title: Text(bookings.length > 1 ? 'Your Tickets' : 'Your Ticket',
            style: const TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              for (final b in bookings) ...[_ticket(b), const SizedBox(height: 16)],
              if (pending.isNotEmpty) _payment(),
              if (pending.isEmpty)
                ElevatedButton.icon(
                  onPressed: () => Navigator.of(context).popUntil((r) => r.isFirst),
                  icon: const Icon(Icons.home, color: Colors.white),
                  label: const Text('Done', style: TextStyle(color: Colors.white, fontSize: 16)),
                  style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade900,
                      minimumSize: const Size.fromHeight(50)),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _ticket(Map<String, dynamic> b) {
    final t = (b['trip_info'] ?? {}) as Map<String, dynamic>;
    final seat = (b['seat_info'] ?? {}) as Map<String, dynamic>;
    final status = b['status'] as String;
    final color = {
          'CONFIRMED': Colors.green,
          'COMPLETED': Colors.blueGrey,
          'CANCELLED': Colors.red,
          'PENDING': Colors.orange,
        }[status] ??
        Colors.grey;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: context.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: context.shadow, blurRadius: 10, spreadRadius: 2)],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('BUS TICKET', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              Chip(
                label: Text(status == 'PENDING' ? 'AWAITING PAYMENT' : status,
                    style: const TextStyle(color: Colors.white, fontSize: 12)),
                backgroundColor: color,
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Opacity(
            opacity: status == 'CONFIRMED' || status == 'COMPLETED' ? 1 : 0.25,
            child: QrImageView(
              data: (b['qr_code'] ?? b['booking_reference']).toString(),
              size: 140,
              backgroundColor: Colors.white,
            ),
          ),
          if (status == 'PENDING')
            const Text('QR code activates after payment',
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 8),
          _row('Ticket ID', b['booking_reference']),
          _row('Passenger', b['passenger_name']),
          _row('Seat', seat['seat_number']),
          const Divider(),
          _row('Company', t['company_name']),
          _row('Bus', '${t['bus_license_plate'] ?? ''} (${t['bus_type'] ?? ''})'),
          _row('From', '${t['origin'] ?? ''} – ${t['origin_terminal'] ?? ''}'),
          _row('To', '${t['destination'] ?? ''} – ${t['destination_terminal'] ?? ''}'),
          const Divider(),
          _row('Date', formatDate(t['departure_date']?.toString())),
          _row('Departure', formatTime(t['departure_time']?.toString())),
          _row('Arrival', formatTime(t['arrival_time']?.toString())),
          const Divider(),
          _row('Price', ugx(b['total_amount'])),
          if (b['payment_info'] != null)
            _row('Paid via', '${b['payment_info']['method']}'.replaceAll('_', ' ')),
        ],
      ),
    );
  }

  Widget _payment() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: context.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: context.shadow, blurRadius: 10, spreadRadius: 2)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Select payment method',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(children: [
            _method('MTN', 'images/mtn.png', 'MTN MoMo'),
            const SizedBox(width: 8),
            _method('AIRTEL', 'images/airtel.jpg', 'Airtel Money'),
            const SizedBox(width: 8),
            _method('CARD', 'images/visa.png', 'Visa'),
          ]),
          const SizedBox(height: 16),
          if (method != 'CARD')
            TextField(
              controller: phoneCtrl,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Mobile money number',
                prefixIcon: Icon(Icons.phone_android),
                border: OutlineInputBorder(),
              ),
            ),
          const SizedBox(height: 8),
          const Text('Sandbox mode: no real money is charged.',
              style: TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: paying ? null : _pay,
            style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                minimumSize: const Size.fromHeight(50)),
            child: paying
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : Text('Pay ${ugx(pendingTotal)}',
                    style: const TextStyle(color: Colors.white, fontSize: 17)),
          ),
        ],
      ),
    );
  }

  Widget _method(String code, String img, String label) {
    final on = method == code;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => method = code),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: on ? context.brand.withOpacity(0.12) : context.surface,
            border: Border.all(color: on ? context.brand : context.shadow, width: on ? 2 : 1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(children: [
            Image.asset(img, height: 34),
            const SizedBox(height: 6),
            Text(label, style: const TextStyle(fontSize: 12), textAlign: TextAlign.center),
          ]),
        ),
      ),
    );
  }

  Widget _row(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
              width: 100,
              child: Text(label, style: const TextStyle(fontWeight: FontWeight.bold))),
          Expanded(child: Text('${value ?? ''}', textAlign: TextAlign.right)),
        ],
      ),
    );
  }
}
