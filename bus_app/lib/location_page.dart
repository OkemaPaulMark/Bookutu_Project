import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';

class LocationPage extends StatefulWidget {
  const LocationPage({super.key});

  @override
  State<LocationPage> createState() => _LocationPageState();
}

class _LocationPageState extends State<LocationPage> {
  GoogleMapController? mapController;
  LatLng myCurrentLocation = const LatLng(0.3152, 32.5816);
  Set<Marker> markers = {};
  Set<Polyline> polylines = {};
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
    _loadBusTerminals();
    _loadRoutes();
  }

  Future<void> _getCurrentLocation() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.whileInUse ||
          permission == LocationPermission.always) {
        Position position = await Geolocator.getCurrentPosition();
        setState(() {
          myCurrentLocation = LatLng(position.latitude, position.longitude);
        });
        _loadBusTerminals();
        
        if (mapController != null) {
          mapController!.animateCamera(
            CameraUpdate.newLatLng(myCurrentLocation),
          );
        }
      }
    } catch (e) {
      print('Error getting location: $e');
    }
  }

  Future<void> _loadBusTerminals() async {
    // Major bus terminals across Uganda regions
    final terminals = [
      // Central Region
      {'name': 'Kampala Central Terminal', 'lat': 0.3152, 'lng': 32.5816},
      {'name': 'Entebbe Terminal', 'lat': 0.0522, 'lng': 32.4634},
      {'name': 'Mukono Terminal', 'lat': 0.3533, 'lng': 32.7574},
      
      // Eastern Region
      {'name': 'Jinja Terminal', 'lat': 0.4244, 'lng': 33.2041},
      {'name': 'Mbale Terminal', 'lat': 1.0827, 'lng': 34.1754},
      {'name': 'Tororo Terminal', 'lat': 0.6928, 'lng': 34.1801},
      {'name': 'Soroti Terminal', 'lat': 1.7147, 'lng': 33.6111},
      
      // Northern Region
      {'name': 'Gulu Terminal', 'lat': 2.7796, 'lng': 32.2993},
      {'name': 'Lira Terminal', 'lat': 2.2491, 'lng': 32.8998},
      {'name': 'Kitgum Terminal', 'lat': 3.2781, 'lng': 32.8864},
      
      // Western Region
      {'name': 'Mbarara Terminal', 'lat': -0.6107, 'lng': 30.6591},
      {'name': 'Fort Portal Terminal', 'lat': 0.6712, 'lng': 30.2747},
      {'name': 'Kasese Terminal', 'lat': 0.1833, 'lng': 30.0833},
      {'name': 'Kabale Terminal', 'lat': -1.2481, 'lng': 29.9894},
      
      // West Nile Region
      {'name': 'Arua Terminal', 'lat': 3.0197, 'lng': 30.9107},
      {'name': 'Nebbi Terminal', 'lat': 2.4786, 'lng': 31.0889},
    ];

    Set<Marker> terminalMarkers = {};
    for (var terminal in terminals) {
      terminalMarkers.add(
        Marker(
          markerId: MarkerId(terminal['name'] as String),
          position: LatLng(terminal['lat'] as double, terminal['lng'] as double),
          infoWindow: InfoWindow(
            title: terminal['name'] as String,
            snippet: 'Bus Terminal',
          ),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        ),
      );
    }

    // Add current location marker
    terminalMarkers.add(
      Marker(
        markerId: const MarkerId('current_location'),
        position: myCurrentLocation,
        infoWindow: const InfoWindow(
          title: 'Your Location',
          snippet: 'Current Position',
        ),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
      ),
    );

    setState(() {
      markers = terminalMarkers;
    });
  }

  Future<void> _loadRoutes() async {
    // Major bus routes across Uganda
    final routes = [
      {
        'name': 'Kampala - Entebbe',
        'points': [LatLng(0.3152, 32.5816), LatLng(0.0522, 32.4634)],
      },
      {
        'name': 'Kampala - Jinja',
        'points': [LatLng(0.3152, 32.5816), LatLng(0.4244, 33.2041)],
      },
      {
        'name': 'Kampala - Mbale',
        'points': [LatLng(0.3152, 32.5816), LatLng(0.4244, 33.2041), LatLng(1.0827, 34.1754)],
      },
      {
        'name': 'Kampala - Gulu',
        'points': [LatLng(0.3152, 32.5816), LatLng(2.7796, 32.2993)],
      },
      {
        'name': 'Kampala - Mbarara',
        'points': [LatLng(0.3152, 32.5816), LatLng(-0.6107, 30.6591)],
      },
      {
        'name': 'Kampala - Arua',
        'points': [LatLng(0.3152, 32.5816), LatLng(2.7796, 32.2993), LatLng(3.0197, 30.9107)],
      },
      {
        'name': 'Kampala - Fort Portal',
        'points': [LatLng(0.3152, 32.5816), LatLng(0.6712, 30.2747)],
      },
    ];

    Set<Polyline> routePolylines = {};
    for (var route in routes) {
      routePolylines.add(
        Polyline(
          polylineId: PolylineId(route['name'] as String),
          points: route['points'] as List<LatLng>,
          color: Colors.blue,
          width: 4,
          patterns: [PatternItem.dash(20), PatternItem.gap(10)],
        ),
      );
    }

    setState(() {
      polylines = routePolylines;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus Routes & Terminals', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location, color: Colors.white),
            onPressed: _getCurrentLocation,
          ),
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: myCurrentLocation,
              zoom: 8.0,
            ),
            onMapCreated: (GoogleMapController controller) {
              mapController = controller;
            },
            markers: markers,
            polylines: polylines,
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
          ),
          if (isLoading)
            const Center(
              child: CircularProgressIndicator(),
            ),
          Positioned(
            top: 20,
            right: 20,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Legend',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.location_on, color: Colors.red, size: 16),
                        const SizedBox(width: 4),
                        const Text('Terminals', style: TextStyle(fontSize: 12)),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.location_on, color: Colors.green, size: 16),
                        const SizedBox(width: 4),
                        const Text('Your Location', style: TextStyle(fontSize: 12)),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 16,
                          height: 2,
                          color: Colors.blue,
                        ),
                        const SizedBox(width: 4),
                        const Text('Routes', style: TextStyle(fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}