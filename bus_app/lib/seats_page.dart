import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';

import 'book_page.dart' show formatDate, formatTime, ugx;
import 'login_screen.dart';
import 'services/api_service.dart';
import 'ticketui.dart';

class SeatSelectionScreen extends StatefulWidget {
  final Map<String, dynamic> trip;
  const SeatSelectionScreen({super.key, required this.trip});

  @override
  State<SeatSelectionScreen> createState() => _SeatSelectionScreenState();
}

class _SeatSelectionScreenState extends State<SeatSelectionScreen> {
  static const _order = ['LEFT_WINDOW', 'LEFT_AISLE', 'RIGHT_AISLE', 'RIGHT_WINDOW'];
  static const maxSeats = 6;

  List<Map<String, dynamic>> seats = [];
  final Map<String, Map<String, dynamic>> selected = {};
  bool loading = true;
  bool booking = false;
  String? error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final data = await ApiService.tripDetails(widget.trip['id']);
      if (!mounted) return;
      setState(() {
        seats = (data['seats'] as List).cast<Map<String, dynamic>>();
        selected.removeWhere((k, _) =>
            !seats.any((s) => s['seat_number'] == k && s['is_available'] == true));
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        loading = false;
        error = e.toString();
      });
    }
  }

  double get total =>
      selected.values.fold(0.0, (sum, s) => sum + ((s['price'] as num?)?.toDouble() ?? 0));

  void _toggle(Map<String, dynamic> seat) {
    if (seat['is_available'] != true) return;
    final n = seat['seat_number'] as String;
    setState(() {
      if (selected.containsKey(n)) {
        selected.remove(n);
      } else if (selected.length < maxSeats) {
        selected[n] = seat;
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('You can book up to $maxSeats seats at a time')));
      }
    });
  }

  Future<void> _book() async {
    setState(() => booking = true);
    try {
      final bookings = await ApiService.createBookings(
          widget.trip['id'], selected.keys.toList());
      if (!mounted) return;
      await Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => TicketScreen(bookings: bookings)),
      );
      selected.clear();
      _load();
    } on AuthRequiredException {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please log in to book your seats')));
      Navigator.push(context, MaterialPageRoute(builder: (_) => const SignInScreen()));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      _load(); // someone may have taken the seat; refresh the map
    } finally {
      if (mounted) setState(() => booking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final trip = widget.trip;
    final rows = <int, Map<String, Map<String, dynamic>>>{};
    for (final s in seats) {
      rows.putIfAbsent(s['row_number'] as int, () => {})[s['seat_position'] as String] = s;
    }
    final rowKeys = rows.keys.toList()..sort();

    return Scaffold(
      appBar: AppBar(
        iconTheme: const IconThemeData(color: Colors.white),
        title: const Text('Select Your Seat', style: TextStyle(color: Colors.white)),
        actions: [IconButton(onPressed: _load, icon: const Icon(Icons.refresh))],
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            color: context.brand.withOpacity(0.10),
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${trip['origin']} → ${trip['destination']}',
                    style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('${trip['company_name']} • ${trip['bus_numberplate']} • '
                    '${formatDate(trip['departure_date'])} ${formatTime(trip['departure_time'])}'),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _legend('Available', Colors.green),
                _legend('Sold', Colors.red.shade400),
                _legend('Selected', Colors.amber),
              ],
            ),
          ),
          Expanded(
            child: loading
                ? const Center(child: CircularProgressIndicator())
                : error != null
                    ? Center(
                        child: Column(mainAxisSize: MainAxisSize.min, children: [
                        Text(error!),
                        TextButton(onPressed: _load, child: const Text('Retry')),
                      ]))
                    : Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 360),
                          child: ListView(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                        color: Colors.blue.shade900,
                                        borderRadius: BorderRadius.circular(8)),
                                    child: const Text('DOOR',
                                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  ),
                                  Icon(Icons.airline_seat_recline_normal,
                                      size: 36, color: context.muted),
                                ],
                              ),
                              const SizedBox(height: 8),
                              for (final r in rowKeys)
                                Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 5),
                                  child: Row(
                                    children: [
                                      _seat(rows[r]![_order[0]]),
                                      const SizedBox(width: 8),
                                      _seat(rows[r]![_order[1]]),
                                      const Spacer(),
                                      _seat(rows[r]![_order[2]]),
                                      const SizedBox(width: 8),
                                      _seat(rows[r]![_order[3]]),
                                    ],
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
          ),
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: context.surface, boxShadow: [
                BoxShadow(color: context.shadow, blurRadius: 6, offset: const Offset(0, -2))
              ]),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Flexible(
                        child: Text(
                            selected.isEmpty
                                ? 'No seat selected'
                                : 'Seats: ${selected.keys.join(', ')}',
                            overflow: TextOverflow.ellipsis),
                      ),
                      Text(ugx(total),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(50),
                      backgroundColor: Colors.blue.shade900,
                    ),
                    onPressed: selected.isEmpty || booking ? null : _book,
                    child: booking
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : Text(
                            selected.isEmpty
                                ? 'Select a seat'
                                : 'Reserve ${selected.length} seat${selected.length > 1 ? 's' : ''}',
                            style: const TextStyle(fontSize: 17, color: Colors.white)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _seat(Map<String, dynamic>? seat) {
    if (seat == null) return const SizedBox(width: 60, height: 48);
    final n = seat['seat_number'] as String;
    final available = seat['is_available'] == true;
    final color = !available
        ? Colors.red.shade400
        : selected.containsKey(n)
            ? Colors.amber
            : Colors.green;
    return GestureDetector(
      onTap: () => _toggle(seat),
      child: Container(
        width: 60,
        height: 48,
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
        child: Center(
          child: Text(n,
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
        ),
      ),
    );
  }

  Widget _legend(String label, Color color) => Row(children: [
        Container(
            width: 18,
            height: 18,
            decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(4))),
        const SizedBox(width: 6),
        Text(label),
      ]);
}
