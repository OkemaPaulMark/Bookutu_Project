import 'dart:async';

import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import 'services/api_service.dart';

/// Live map of buses on the road (OpenStreetMap tiles, no API key needed).
class LocationPage extends StatefulWidget {
  const LocationPage({super.key});

  @override
  State<LocationPage> createState() => _LocationPageState();
}

class _LocationPageState extends State<LocationPage> {
  final mapController = MapController();
  Timer? _timer;

  List<Map<String, dynamic>> buses = [];
  List<Map<String, dynamic>> routes = [];
  List<Map<String, dynamic>> terminals = [];
  LatLng? me;
  int? selectedTrip;
  String? error;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _load();
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.mapData();
      if (!mounted) return;
      setState(() {
        buses = (data['buses'] as List).cast<Map<String, dynamic>>();
        routes = (data['routes'] as List).cast<Map<String, dynamic>>();
        terminals = (data['terminals'] as List).cast<Map<String, dynamic>>();
        error = null;
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = 'Could not load live buses';
        loading = false;
      });
    }
  }

  Future<void> _locateMe() async {
    try {
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) perm = await Geolocator.requestPermission();
      if (perm == LocationPermission.denied || perm == LocationPermission.deniedForever) {
        throw 'Location permission denied';
      }
      final p = await Geolocator.getCurrentPosition();
      final pos = LatLng(p.latitude, p.longitude);
      setState(() => me = pos);
      mapController.move(pos, 12);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Could not get your location: $e')));
    }
  }

  void _focusBus(Map<String, dynamic> b) {
    setState(() => selectedTrip = b['trip_id']);
    mapController.move(LatLng(b['lat'], b['lng']), 10);
  }

  @override
  Widget build(BuildContext context) {
    final moving = buses.where((b) => b['state'] == 'IN_TRANSIT').length;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Location', style: TextStyle(color: Colors.white)),
        actions: [
          IconButton(
              onPressed: _load,
              icon: const Icon(Icons.refresh, color: Colors.white),
              tooltip: 'Refresh'),
        ],
      ),
      body: Stack(
        children: [
          FlutterMap(
            mapController: mapController,
            options: const MapOptions(
              initialCenter: LatLng(1.2, 32.3),
              initialZoom: 7,
              minZoom: 5,
              maxZoom: 18,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.bookutu.bus_app',
                // Darken OSM tiles in dark mode
                tileBuilder: context.isDark ? darkModeTileBuilder : null,
              ),
              PolylineLayer(
                polylines: [
                  for (final r in routes)
                    Polyline(
                      points: [
                        for (final p in r['points'] as List)
                          LatLng((p['lat'] as num).toDouble(), (p['lng'] as num).toDouble())
                      ],
                      strokeWidth: 4,
                      color: Colors.blue.shade700.withOpacity(0.55),
                    ),
                ],
              ),
              MarkerLayer(
                markers: [
                  for (final t in terminals)
                    Marker(
                      point: LatLng((t['lat'] as num).toDouble(), (t['lng'] as num).toDouble()),
                      width: 120,
                      height: 44,
                      child: Column(children: [
                        const Icon(Icons.location_city, color: Colors.deepPurple, size: 22),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          color: context.surface.withOpacity(0.8),
                          child: Text(t['city'],
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                        ),
                      ]),
                    ),
                  for (final b in buses)
                    Marker(
                      point: LatLng((b['lat'] as num).toDouble(), (b['lng'] as num).toDouble()),
                      width: 40,
                      height: 40,
                      child: GestureDetector(
                        onTap: () => _focusBus(b),
                        child: Container(
                          decoration: BoxDecoration(
                            color: b['state'] == 'IN_TRANSIT' ? Colors.green.shade700 : Colors.orange,
                            shape: BoxShape.circle,
                            border: Border.all(
                                color: selectedTrip == b['trip_id'] ? Colors.yellow : Colors.white,
                                width: 3),
                            boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 4)],
                          ),
                          child: const Icon(Icons.directions_bus, color: Colors.white, size: 20),
                        ),
                      ),
                    ),
                  if (me != null)
                    Marker(
                      point: me!,
                      width: 24,
                      height: 24,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.blue,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                        ),
                      ),
                    ),
                ],
              ),
              const RichAttributionWidget(
                attributions: [TextSourceAttribution('OpenStreetMap contributors')],
              ),
            ],
          ),
          Positioned(
            top: 12,
            left: 12,
            right: 12,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: loading
                    ? const LinearProgressIndicator()
                    : Text(
                        error ??
                            '$moving bus${moving == 1 ? '' : 'es'} on the road • '
                                '${buses.length - moving} waiting to depart today',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
              ),
            ),
          ),
          Positioned(
            right: 12,
            bottom: 200,
            child: FloatingActionButton.small(
              heroTag: 'me',
              onPressed: _locateMe,
              backgroundColor: context.surface,
              child: Icon(Icons.my_location, color: context.brand),
            ),
          ),
          DraggableScrollableSheet(
            initialChildSize: 0.22,
            minChildSize: 0.1,
            maxChildSize: 0.6,
            builder: (context, scroll) => Container(
              decoration: BoxDecoration(
                color: context.surface,
                borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
                boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)],
              ),
              child: ListView.builder(
                controller: scroll,
                itemCount: buses.length + 1,
                itemBuilder: (_, i) {
                  if (i == 0) {
                    return Column(children: [
                      const SizedBox(height: 8),
                      Container(
                          width: 40,
                          height: 4,
                          decoration: BoxDecoration(
                              color: Colors.grey.shade400,
                              borderRadius: BorderRadius.circular(2))),
                      const Padding(
                        padding: EdgeInsets.all(10),
                        child: Text("Today's buses",
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                    ]);
                  }
                  final b = buses[i - 1];
                  final transit = b['state'] == 'IN_TRANSIT';
                  return ListTile(
                    selected: selectedTrip == b['trip_id'],
                    onTap: () => _focusBus(b),
                    leading: CircleAvatar(
                      backgroundColor: transit ? Colors.green.shade700 : Colors.orange,
                      child: const Icon(Icons.directions_bus, color: Colors.white),
                    ),
                    title: Text(b['route']),
                    subtitle: Text('${b['company']} • ${b['plate']} • '
                        '${b['departure_time']}–${b['arrival_time']}'),
                    trailing: transit
                        ? SizedBox(
                            width: 56,
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text('${b['progress']}%'),
                                const SizedBox(height: 4),
                                LinearProgressIndicator(value: (b['progress'] as num) / 100),
                              ],
                            ),
                          )
                        : const Text('Waiting', style: TextStyle(color: Colors.orange)),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
