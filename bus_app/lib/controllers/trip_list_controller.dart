import 'package:flutter/foundation.dart';

import '../models/trip.dart';
import '../services/trip_service.dart';

class TripListController extends ChangeNotifier {
  final TripService _tripService;

  TripListController({TripService? tripService}) : _tripService = tripService ?? TripService();

  List<Trip> _trips = [];
  bool _isLoading = true;
  String _searchText = '';
  String? _errorMessage;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Trip> get filteredTrips {
    if (_searchText.isEmpty) return _trips;
    return _trips
        .where((trip) => trip.routeName.toLowerCase().contains(_searchText.toLowerCase()))
        .toList();
  }

  Future<void> loadTrips() async {
    _isLoading = true;
    notifyListeners();
    try {
      _trips = await _tripService.fetchTrips();
      _errorMessage = null;
    } catch (e) {
      _errorMessage = 'Failed to connect to server: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void updateSearch(String value) {
    _searchText = value;
    notifyListeners();
  }
}
