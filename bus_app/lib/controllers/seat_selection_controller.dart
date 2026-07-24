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

  String? seatIdFor(int seatNumber) => _seatMap.seatIdFor(seatNumber);
  String? seatLabelFor(int seatNumber) => _seatMap.seatLabelFor(seatNumber);

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
    final seatNumbers = selectedSeats.toList();
    final seatIds = seatNumbers.map((n) => seatIdFor(n)).whereType<String>().toList();
    final seatLabels = seatNumbers.map((n) => seatLabelFor(n)).whereType<String>().toList();
    if (seatIds.length != seatNumbers.length || seatLabels.length != seatNumbers.length) {
      _errorMessage = 'Seat data is out of date, please go back and try again.';
      return null;
    }

    final passengerName = [user?.firstName, user?.lastName]
        .where((part) => part != null && part.isNotEmpty)
        .join(' ');

    return Booking.preview(
      seatNumbers: seatNumbers,
      seatIds: seatIds,
      seatLabels: seatLabels,
      passengerName: passengerName.isNotEmpty ? passengerName : (user?.username ?? user?.email ?? 'Passenger'),
      passengerPhone: user?.phoneNumber ?? '',
      seatPrice: seatPrice,
    );
  }
}
