import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String _baseUrl = 'http://127.0.0.1:8000/api/'; // Replace with your backend URL

  Future<List<dynamic>> fetchRoutes(String token) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/bookings/direct-booking-routes/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['routes'];
    } else {
      throw Exception('Failed to load routes: ${response.body}');
    }
  }

  Future<List<dynamic>> fetchTrips(String token, int routeId, String departureDate) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/bookings/direct-booking-trips/?route_id=$routeId&departure_date=$departureDate'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['trips'];
    } else {
      throw Exception('Failed to load trips: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> fetchSeats(String token, int tripId) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/bookings/direct-booking-seats/$tripId/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load seats: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> createBooking(String token, Map<String, dynamic> bookingData) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/bookings/direct-booking-create/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: json.encode(bookingData),
    );

    if (response.statusCode == 201) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to create booking: ${response.body}');
    }
  }
}
