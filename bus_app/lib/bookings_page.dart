import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';

import 'book_page.dart' show formatDate, formatTime, ugx;
import 'login_screen.dart';
import 'services/api_service.dart';
import 'ticketui.dart';

class BookingsPage extends StatefulWidget {
  const BookingsPage({super.key});

  @override
  State<BookingsPage> createState() => _BookingsPageState();
}

class _BookingsPageState extends State<BookingsPage> {
  List<Map<String, dynamic>> bookings = [];
  bool loading = true;
  String? error;
  bool needsLogin = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      error = null;
      needsLogin = false;
    });
    try {
      final data = await ApiService.myBookings();
      if (!mounted) return;
      setState(() {
        bookings = data.cast<Map<String, dynamic>>();
        loading = false;
      });
    } on AuthRequiredException {
      if (!mounted) return;
      setState(() {
        loading = false;
        needsLogin = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        loading = false;
        error = e.toString();
      });
    }
  }

  bool _isUpcoming(Map<String, dynamic> b) =>
      (b['status'] == 'PENDING' || b['status'] == 'CONFIRMED') &&
      !DateTime.parse(b['trip_info']['departure_date'])
          .isBefore(DateTime.now().subtract(const Duration(days: 1)));

  Future<void> _cancel(Map<String, dynamic> b) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Cancel booking?'),
        content: Text('Seat ${b['seat_info']?['seat_number']} on '
            '${b['trip_info']['route']} will be released.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Keep')),
          TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Cancel booking', style: TextStyle(color: Colors.red))),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await ApiService.cancelBooking(b['id']);
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Booking cancelled')));
      _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    final upcoming = bookings.where(_isUpcoming).toList();
    final past = bookings.where((b) => !_isUpcoming(b)).toList();
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: context.pageBg,
        appBar: AppBar(
          title: const Text('My Bookings', style: TextStyle(color: Colors.white)),
          iconTheme: const IconThemeData(color: Colors.white),
          bottom: TabBar(
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            indicatorColor: Colors.white,
            tabs: [Tab(text: 'Upcoming (${upcoming.length})'), Tab(text: 'Past (${past.length})')],
          ),
        ),
        body: loading
            ? const Center(child: CircularProgressIndicator())
            : needsLogin
                ? Center(
                    child: ElevatedButton(
                      onPressed: () => Navigator.push(
                          context, MaterialPageRoute(builder: (_) => const SignInScreen())),
                      child: const Text('Log in to see your bookings'),
                    ),
                  )
                : error != null
                    ? Center(child: Text(error!))
                    : TabBarView(children: [_list(upcoming, true), _list(past, false)]),
      ),
    );
  }

  Widget _list(List<Map<String, dynamic>> items, bool upcoming) {
    return RefreshIndicator(
      onRefresh: _load,
      child: items.isEmpty
          ? ListView(children: [
              Padding(
                padding: const EdgeInsets.all(48),
                child: Text(upcoming ? 'No upcoming trips. Book one from the Book tab!' : 'No past bookings.',
                    textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey, fontSize: 16)),
              )
            ])
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: items.length,
              itemBuilder: (_, i) => _card(items[i], upcoming),
            ),
    );
  }

  Widget _card(Map<String, dynamic> b, bool upcoming) {
    final t = b['trip_info'] as Map<String, dynamic>;
    final status = b['status'] as String;
    final color = {
          'CONFIRMED': Colors.green,
          'COMPLETED': Colors.blueGrey,
          'CANCELLED': Colors.red,
          'PENDING': Colors.orange,
        }[status] ??
        Colors.grey;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () async {
          await Navigator.push(
              context, MaterialPageRoute(builder: (_) => TicketScreen(bookings: [b])));
          _load();
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(
                  child: Text(t['route'] ?? '',
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                      color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(20)),
                  child: Text(status == 'PENDING' ? 'UNPAID' : status,
                      style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12)),
                ),
              ]),
              const SizedBox(height: 6),
              Text('${t['company_name']} • ${t['bus_license_plate']}'),
              Text('${formatDate(t['departure_date']?.toString())} at '
                  '${formatTime(t['departure_time']?.toString())} • Seat ${b['seat_info']?['seat_number'] ?? '-'}'),
              const SizedBox(height: 6),
              Row(children: [
                Text(ugx(b['total_amount']), style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(width: 8),
                Text(b['booking_reference'] ?? '',
                    style: TextStyle(color: context.muted, fontSize: 12)),
                const Spacer(),
                if (upcoming)
                  TextButton(
                    onPressed: () => _cancel(b),
                    child: const Text('Cancel', style: TextStyle(color: Colors.red)),
                  ),
                if (status == 'PENDING')
                  TextButton(
                    onPressed: () async {
                      await Navigator.push(context,
                          MaterialPageRoute(builder: (_) => TicketScreen(bookings: [b])));
                      _load();
                    },
                    child: const Text('Pay now'),
                  ),
              ]),
            ],
          ),
        ),
      ),
    );
  }
}
