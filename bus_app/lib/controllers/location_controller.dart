import 'package:flutter/foundation.dart';

import '../models/bus_route.dart';
import '../models/bus_terminal.dart';
import '../services/location_service.dart';

class LocationController extends ChangeNotifier {
  final LocationService _locationService;

  LocationController({LocationService? locationService})
      : _locationService = locationService ?? LocationService();

  LatLngPoint currentPosition = const LatLngPoint(0.3152, 32.5816);
  List<BusTerminal> terminals = [];
  List<BusRoute> routes = [];
  bool isLoading = true;

  Future<void> load() async {
    terminals = _locationService.busTerminals;
    routes = _locationService.busRoutes;
    await refreshCurrentPosition();
    isLoading = false;
    notifyListeners();
  }

  Future<void> refreshCurrentPosition() async {
    try {
      final position = await _locationService.getCurrentPosition();
      if (position != null) {
        currentPosition = position;
      }
    } catch (_) {
      // Keep the default/last-known position if location retrieval fails.
    }
    notifyListeners();
  }
}
