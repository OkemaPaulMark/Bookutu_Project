import 'package:flutter/foundation.dart';

import '../models/booking.dart';
import '../models/seat_map.dart';
import '../services/auth_service.dart';
import '../services/trip_service.dart';

enum SeatStatus { available, selected, booked }

class SeatSelectionController extends ChangeNotifier {
  final TripService _tripService;
  final AuthService _authService;

  SeatSelectionController({TripService? tripService, AuthService? authService})
      : _tripService = tripService ?? TripService(),
        _authService = authService ?? AuthService();

  final Set<int> selectedSeats = {};
  SeatMap _seatMap = SeatMap.defaults();
  bool _isLoading = true;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int get busCapacity => _seatMap.busCapacity;
  double get seatPrice => _seatMap.seatPrice;

  SeatStatus statusFor(int seatNumber) {
    if (_seatMap.bookedSeats.contains(seatNumber)) return SeatStatus.booked;
    if (selectedSeats.contains(seatNumber)) return SeatStatus.selected;
    return SeatStatus.available;
  }

  Future<void> loadSeatMap(String tripId) async {
    _isLoading = true;
    notifyListeners();
    try {
      _seatMap = await _tripService.fetchSeatMap(tripId);
      _errorMessage = null;
    } catch (e) {
      _errorMessage = 'Error loading seats: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void toggleSeat(int seatNumber) {
    if (_seatMap.bookedSeats.contains(seatNumber)) return;
    if (selectedSeats.contains(seatNumber)) {
      selectedSeats.remove(seatNumber);
    } else {
      selectedSeats.add(seatNumber);
    }
    notifyListeners();
  }

  Future<Booking?> buildPreview() async {
    if (selectedSeats.isEmpty) return null;
    final user = await _authService.getUserData();
    return Booking.preview(
      seatNumbers: selectedSeats.toList(),
      passengerName: user?.username ?? 'User',
      seatPrice: seatPrice,
    );
  }
}
