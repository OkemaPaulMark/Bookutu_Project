import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:intl/intl.dart';

import 'seats_page.dart';
import 'services/api_service.dart';

String formatTime(String? hhmmss) {
  if (hhmmss == null || hhmmss.isEmpty) return '';
  final parts = hhmmss.split(':');
  final t = TimeOfDay(hour: int.parse(parts[0]), minute: int.parse(parts[1]));
  final h = t.hourOfPeriod == 0 ? 12 : t.hourOfPeriod;
  return '$h:${parts[1]} ${t.period == DayPeriod.am ? 'AM' : 'PM'}';
}

String formatDate(String? iso) {
  if (iso == null || iso.isEmpty) return '';
  final d = DateTime.parse(iso);
  final today = DateTime.now();
  final diff = DateTime(d.year, d.month, d.day)
      .difference(DateTime(today.year, today.month, today.day))
      .inDays;
  if (diff == 0) return 'Today';
  if (diff == 1) return 'Tomorrow';
  return DateFormat('EEE, d MMM').format(d);
}

final _money = NumberFormat.decimalPattern();
String ugx(dynamic amount) =>
    'UGX ${_money.format(double.tryParse(amount.toString())?.round() ?? 0)}';

class BusListScreen extends StatefulWidget {
  const BusListScreen({super.key});

  @override
  State<BusListScreen> createState() => _BusListScreenState();
}

class _BusListScreenState extends State<BusListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchText = '';
  List<Map<String, dynamic>> trips = [];
  bool isLoading = true;
  String? error;
  DateTime? _date;

  @override
  void initState() {
    super.initState();
    fetchTrips();
    _searchController.addListener(() {
      setState(() => _searchText = _searchController.text);
    });
  }

  Future<void> fetchTrips() async {
    setState(() {
      isLoading = trips.isEmpty;
      error = null;
    });
    try {
      final data = await ApiService.trips(
          date: _date == null ? null : DateFormat('yyyy-MM-dd').format(_date!));
      if (!mounted) return;
      setState(() {
        trips = data.cast<Map<String, dynamic>>();
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        isLoading = false;
        error = 'Could not reach the server. Pull down to retry.\n($e)';
      });
    }
  }

  List<Map<String, dynamic>> get filteredTrips {
    final q = _searchText.trim().toLowerCase();
    if (q.isEmpty) return trips;
    return trips.where((t) {
      final hay = '${t['route_name']} ${t['origin']} ${t['destination']} ${t['company_name']}'
          .toLowerCase();
      return q.split(RegExp(r'\s+')).every(hay.contains);
    }).toList();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _date ?? now,
      firstDate: DateTime(now.year, now.month, now.day),
      lastDate: now.add(const Duration(days: 60)),
      helpText: 'Travel date',
    );
    if (picked != null) {
      setState(() {
        _date = picked;
        trips = [];
      });
      fetchTrips();
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final list = filteredTrips;
    return Scaffold(
      backgroundColor: context.pageBg,
      appBar: AppBar(
        title: const Text('Book a Bus', style: TextStyle(color: Colors.white)),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60.0),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search e.g. "Kampala Gulu" or company',
                filled: true,
                fillColor: context.surface,
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide.none,
                ),
                prefixIcon: const Icon(Icons.search),
              ),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          if (_date != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Align(
                alignment: Alignment.centerLeft,
                child: InputChip(
                  avatar: const Icon(Icons.event, size: 18),
                  label: Text('Trips on ${DateFormat('EEE, d MMM').format(_date!)}'),
                  onDeleted: () {
                    setState(() => _date = null);
                    fetchTrips();
                  },
                ),
              ),
            ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: fetchTrips,
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : error != null
                      ? ListView(children: [
                          Padding(
                            padding: const EdgeInsets.all(32),
                            child: Text(error!, textAlign: TextAlign.center),
                          )
                        ])
                      : list.isEmpty
                          ? ListView(children: const [
                              Padding(
                                padding: EdgeInsets.all(48),
                                child: Text('No trips found',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(color: Colors.grey, fontSize: 16)),
                              )
                            ])
                          : ListView.builder(
                              padding: const EdgeInsets.fromLTRB(12, 12, 12, 88),
                              itemCount: list.length,
                              itemBuilder: (context, i) => TripCard(trip: list[i], onReturn: fetchTrips),
                            ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _pickDate,
        backgroundColor: Colors.blue.shade900,
        label: const Text('Book for later', style: TextStyle(color: Colors.white)),
        icon: const Icon(Icons.schedule, color: Colors.white),
      ),
    );
  }
}

class TripCard extends StatelessWidget {
  final Map<String, dynamic> trip;
  final VoidCallback? onReturn;

  const TripCard({super.key, required this.trip, this.onReturn});

  @override
  Widget build(BuildContext context) {
    final seatsLeft = trip['seats_left'] ?? 0;
    final image = trip['bus_image'] as String?;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: seatsLeft > 0 ? () => _open(context) : null,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 110,
              height: 150,
              child: image != null
                  ? Image.network(image,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) =>
                          Image.asset('images/bus.jpg', fit: BoxFit.cover))
                  : Image.asset('images/bus.jpg', fit: BoxFit.cover),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '${trip['origin']} → ${trip['destination']}',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(ugx(trip['base_fare']),
                            style: TextStyle(
                                fontWeight: FontWeight.bold, color: context.brand)),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text('${trip['company_name']} • ${trip['bus_type']} • ${trip['bus_numberplate']}',
                        style: TextStyle(color: context.muted, fontSize: 12),
                        overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 6),
                    Row(children: [
                      const Icon(Icons.event, size: 14, color: Colors.grey),
                      const SizedBox(width: 4),
                      Text(formatDate(trip['departure_date']), style: const TextStyle(fontSize: 13)),
                      const SizedBox(width: 10),
                      const Icon(Icons.schedule, size: 14, color: Colors.grey),
                      const SizedBox(width: 4),
                      Flexible(
                        child: Text(
                            '${formatTime(trip['departure_time'])} – ${formatTime(trip['arrival_time'])}',
                            style: const TextStyle(fontSize: 13),
                            overflow: TextOverflow.ellipsis),
                      ),
                    ]),
                    const SizedBox(height: 4),
                    Text('From ${trip['origin_terminal'] ?? ''}',
                        style: TextStyle(color: context.muted, fontSize: 12),
                        overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(Icons.event_seat,
                            size: 16, color: seatsLeft < 10 ? Colors.orange : Colors.green),
                        const SizedBox(width: 4),
                        Text(seatsLeft > 0 ? '$seatsLeft seats left' : 'Fully booked',
                            style: TextStyle(
                                fontSize: 13,
                                color: seatsLeft < 10 ? Colors.orange.shade800 : Colors.green.shade800)),
                        const Spacer(),
                        SizedBox(
                          height: 32,
                          child: ElevatedButton(
                            onPressed: seatsLeft > 0 ? () => _open(context) : null,
                            style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue.shade900,
                                padding: const EdgeInsets.symmetric(horizontal: 14)),
                            child: const Text('Book Now', style: TextStyle(color: Colors.white)),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _open(BuildContext context) async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => SeatSelectionScreen(trip: trip)),
    );
    onReturn?.call(); // seat counts may have changed
  }
}
