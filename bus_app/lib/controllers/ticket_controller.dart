import 'package:flutter/foundation.dart';

import '../models/booking.dart';
import '../models/trip.dart';
import '../services/booking_service.dart';
import '../services/notification_service.dart';

class TicketController extends ChangeNotifier {
  final BookingService _bookingService;

  TicketController({BookingService? bookingService}) : _bookingService = bookingService ?? BookingService();

  bool _isLoading = false;
  bool _isBookingConfirmed = false;
  Booking? _confirmedBooking;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  bool get isBookingConfirmed => _isBookingConfirmed;
  Booking? get confirmedBooking => _confirmedBooking;
  String? get errorMessage => _errorMessage;

  String ticketId(Booking preview) {
    final source = _confirmedBooking ?? preview;
    return source.bookingReference ??
        'TKT-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}';
  }

  Future<bool> confirmBooking({required Trip trip, required Booking preview}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _confirmedBooking = await _bookingService.confirmBooking(trip: trip, preview: preview);
      _isBookingConfirmed = true;
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> saveToNotifications({required Booking preview, required Trip trip}) {
    return NotificationService.saveTicket(
      bookingData: _confirmedBooking ?? preview,
      tripData: trip,
    );
  }
}
