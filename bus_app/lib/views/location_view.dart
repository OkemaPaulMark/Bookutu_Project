import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:provider/provider.dart';

import '../controllers/location_controller.dart';
import '../models/bus_route.dart';

class LocationPage extends StatelessWidget {
  const LocationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<LocationController>(
      create: (_) => LocationController(),
      child: const _LocationView(),
    );
  }
}

class _LocationView extends StatefulWidget {
  const _LocationView();

  @override
  State<_LocationView> createState() => _LocationViewState();
}

class _LocationViewState extends State<_LocationView> {
  GoogleMapController? _mapController;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<LocationController>().load();
    });
  }

  Future<void> _recenter() async {
    final controller = context.read<LocationController>();
    await controller.refreshCurrentPosition();
    if (_mapController != null) {
      final pos = controller.currentPosition;
      _mapController!.animateCamera(CameraUpdate.newLatLng(LatLng(pos.lat, pos.lng)));
    }
  }

  Set<Marker> _buildMarkers(LocationController controller) {
    final markers = controller.terminals
        .map((terminal) => Marker(
              markerId: MarkerId(terminal.name),
              position: LatLng(terminal.lat, terminal.lng),
              infoWindow: InfoWindow(title: terminal.name, snippet: 'Bus Terminal'),
              icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
            ))
        .toSet();

    markers.add(
      Marker(
        markerId: const MarkerId('current_location'),
        position: LatLng(controller.currentPosition.lat, controller.currentPosition.lng),
        infoWindow: const InfoWindow(title: 'Your Location', snippet: 'Current Position'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
      ),
    );

    return markers;
  }

  Set<Polyline> _buildPolylines(List<BusRoute> routes) {
    return routes
        .map((route) => Polyline(
              polylineId: PolylineId(route.name),
              points: route.points.map((p) => LatLng(p.lat, p.lng)).toList(),
              color: Colors.blue,
              width: 4,
              patterns: [PatternItem.dash(20), PatternItem.gap(10)],
            ))
        .toSet();
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<LocationController>();
    final currentPosition = LatLng(controller.currentPosition.lat, controller.currentPosition.lng);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus Routes & Terminals', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location, color: Colors.white),
            onPressed: _recenter,
          ),
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(target: currentPosition, zoom: 8.0),
            onMapCreated: (mapController) => _mapController = mapController,
            markers: _buildMarkers(controller),
            polylines: _buildPolylines(controller.routes),
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
          ),
          if (controller.isLoading) const Center(child: CircularProgressIndicator()),
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
                    const Text('Legend', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.location_on, color: Colors.red, size: 16),
                        const SizedBox(width: 4),
                        const Text('Terminals', style: TextStyle(fontSize: 12)),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.location_on, color: Colors.green, size: 16),
                        const SizedBox(width: 4),
                        const Text('Your Location', style: TextStyle(fontSize: 12)),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(width: 16, height: 2, color: Colors.blue),
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
