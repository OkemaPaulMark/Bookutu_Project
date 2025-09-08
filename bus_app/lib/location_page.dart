import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class LocationPage extends StatefulWidget {
  const LocationPage({super.key});

  @override
  State<LocationPage> createState() => _LocationPageState();
}

class _LocationPageState extends State<LocationPage> {
  LatLng myCurrentLocation = const LatLng(0.3152, 32.5816);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Location', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
      ),
      body: Stack(
        children: [
          // Google Map as the background
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: myCurrentLocation,
              zoom: 14.0,
            ),
          ),
          
          // Draggable bottom sheet
          
        ],
      ),
    );
  }
}