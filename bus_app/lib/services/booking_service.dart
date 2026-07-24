import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/booking.dart';
import '../models/passenger_booking.dart';
import '../models/trip.dart';
import 'auth_service.dart';

const String _baseUrl = String.fromEnvironment(
  'BOOKUTU_API_URL',
  defaultValue: 'http://192.168.115.75:8001',
);
const String _apiUrl = '$_baseUrl/api/v1';
const String _bookingsEndpoint = '$_apiUrl/bookings';

class BookingService {
  final AuthService _authService;

  BookingService({AuthService? authService}) : _authService = authService ?? AuthService();

  Future<Booking> confirmBooking({required Trip trip, required Booking preview}) async {
    final seatIds = preview.seatIds;
    if (seatIds == null || seatIds.isEmpty) {
      throw Exception('No seats selected');
    }

    final token = await _authService.getAccessToken();
    final user = await _authService.getUserData();

    final bookings = <Booking>[];
    for (var i = 0; i < seatIds.length; i++) {
      final response = await http.post(
        Uri.parse(_bookingsEndpoint),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'trip_id': trip.id,
          'seat_id': seatIds[i],
          'passenger_name': preview.passengerName,
          'passenger_phone': user?.phoneNumber ?? '',
        }),
      );

      final data = json.decode(response.body) as Map<String, dynamic>;

      if (response.statusCode == 200 || response.statusCode == 201) {
        bookings.add(Booking.fromBookingResponse(data, seatNumber: preview.seatNumbers[i]));
      } else {
        throw Exception(_extractError(data, preview.seatNumbers[i]));
      }
    }

    return Booking.combine(bookings);
  }

  // Reads a readable message out of a DRF error response, which is either
  // {"detail": "..."} or a field-validation dict like {"passengerPhone": ["..."]}.
  String _extractError(Map<String, dynamic> data, int seatNumber) {
    if (data['detail'] != null) return data['detail'].toString();
    if (data['message'] != null) return data['message'].toString();

    for (final value in data.values) {
      if (value is List && value.isNotEmpty) return value.first.toString();
      if (value is String) return value;
    }

    return 'Booking failed for seat $seatNumber';
  }

  Future<List<PassengerBooking>> fetchMyBookings() async {
    final token = await _authService.getAccessToken();
    final response = await http
        .get(Uri.parse(_bookingsEndpoint), headers: {if (token != null) 'Authorization': 'Bearer $token'})
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw Exception('Failed to load bookings: ${response.statusCode}');
    }

    final body = json.decode(response.body) as Map<String, dynamic>;
    final data = body['data'] as List<dynamic>;
    return data.map((item) => PassengerBooking.fromJson(item as Map<String, dynamic>)).toList();
  }
}
