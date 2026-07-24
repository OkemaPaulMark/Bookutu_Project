import 'package:flutter/foundation.dart';

import '../models/passenger_booking.dart';
import '../services/booking_service.dart';

class BookingsController extends ChangeNotifier {
  final BookingService _bookingService;

  BookingsController({BookingService? bookingService}) : _bookingService = bookingService ?? BookingService() {
    loadBookings();
  }

  bool _isLoading = true;
  String? _errorMessage;
  List<PassengerBooking> _bookings = [];

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<PassengerBooking> get bookings => _bookings;

  Future<void> loadBookings() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _bookings = await _bookingService.fetchMyBookings();
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
