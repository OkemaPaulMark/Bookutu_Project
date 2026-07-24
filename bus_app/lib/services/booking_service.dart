import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/booking.dart';
import '../models/trip.dart';
import 'auth_service.dart';

const String _baseUrl = String.fromEnvironment(
  'BOOKUTU_API_URL',
  defaultValue: 'http://10.0.2.2:4000',
);
const String _apiUrl = '$_baseUrl/api/v1';
const String _bookingsEndpoint = '$_apiUrl/bookings';

class BookingService {
  final AuthService _authService;

  BookingService({AuthService? authService}) : _authService = authService ?? AuthService();

  Future<Booking> confirmBooking({required Trip trip, required Booking preview}) async {
    final token = await _authService.getAccessToken();

    final response = await http.post(
      Uri.parse(_bookingsEndpoint),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: json.encode({
        'trip_id': trip.id,
        'seat_numbers': preview.seatNumbers,
        'passenger_name': preview.passengerName,
        'passenger_phone': '0700000000',
      }),
    );

    final data = json.decode(response.body) as Map<String, dynamic>;

    if (response.statusCode == 200 || response.statusCode == 201) {
      return Booking.fromJson(data);
    }

    throw Exception(data['error'] ?? data['message'] ?? 'Booking failed');
  }
}
