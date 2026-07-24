import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/seat_map.dart';
import '../models/trip.dart';
import 'auth_service.dart';

const String _baseUrl = String.fromEnvironment(
  'BOOKUTU_API_URL',
  defaultValue: 'http://192.168.115.75:8001',
);
const String _apiUrl = '$_baseUrl/api/v1';
const String _tripsEndpoint = '$_apiUrl/trips';
String _tripSeatsEndpoint(String tripId) => '$_apiUrl/trips/$tripId/seats';

class TripService {
  final AuthService _authService;

  TripService({AuthService? authService}) : _authService = authService ?? AuthService();

  Future<Map<String, String>> _authHeaders() async {
    final token = await _authService.getAccessToken();
    return {if (token != null) 'Authorization': 'Bearer $token'};
  }

  Future<List<Trip>> fetchTrips() async {
    final response = await http
        .get(Uri.parse(_tripsEndpoint), headers: await _authHeaders())
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw Exception('Failed to load trips: ${response.statusCode}');
    }

    final Map<String, dynamic> body = json.decode(response.body) as Map<String, dynamic>;
    final List<dynamic> data = body['data'] as List<dynamic>;
    return data.map((item) => Trip.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<SeatMap> fetchSeatMap(String tripId) async {
    final response = await http.get(Uri.parse(_tripSeatsEndpoint(tripId)), headers: await _authHeaders());

    if (response.statusCode != 200) {
      throw Exception('Failed to load seat map: ${response.statusCode}');
    }

    return SeatMap.fromJson(json.decode(response.body) as Map<String, dynamic>);
  }
}
