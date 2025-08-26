import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class LocationPage extends StatefulWidget {
  const LocationPage({super.key});

  @override
  State<LocationPage> createState() => _LocationPageState();
}

class _LocationPageState extends State<LocationPage> {
  LatLng myCurrentLocation = const LatLng(0.3152, 32.5816);
  final DraggableScrollableController _sheetController = DraggableScrollableController();

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
          DraggableScrollableSheet(
            controller: _sheetController,
            initialChildSize: 0.15, // 15% of screen height when collapsed
            minChildSize: 0.15,    // Minimum 15% of screen height
            maxChildSize: 0.6,     // Maximum 70% of screen height when expanded
            snap: true,
            snapSizes: const [0.15, 0.5, 0.6],
            builder: (BuildContext context, ScrollController scrollController) {
              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 10,
                      spreadRadius: 1,
                    ),
                  ],
                ),
                child: SingleChildScrollView(
                  controller: scrollController,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Drag handle
                      Center(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8.0),
                          child: Container(
                            width: 40,
                            height: 5,
                            decoration: BoxDecoration(
                              color: Colors.grey.shade400,
                              borderRadius: BorderRadius.circular(5),
                            ),
                          ),
                        ),
                      ),
                      
                      // Sheet content
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16.0),
                        child: Text(
                          'Available Buses',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      
                      // Example list of buses
                      ListView.builder(
                        controller: scrollController,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: 5,
                        itemBuilder: (context, index) {
                          return ListTile(
                            leading: const Icon(Icons.directions_bus, color: Colors.blue),
                            title: Text('Bus ${index + 1}'),
                            subtitle: const Text('Next arrival: 10 mins'),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () {
                              // Handle bus selection
                            },
                          );
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}