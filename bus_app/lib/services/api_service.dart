import 'dart:convert';

import 'package:bus_app/config.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Thrown when an endpoint needs a logged-in user and there is no valid token.
class AuthRequiredException implements Exception {
  @override
  String toString() => 'Please log in to continue';
}

/// Error returned by the backend, with a human-readable message.
class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

/// Thin client for the Django mobile API (`/api/auth/...`).
class ApiService {
  static final String base = '$apiHost/api/auth';

  static Future<Map<String, String>> _headers({bool auth = false}) async {
    final headers = {'Content-Type': 'application/json'};
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    } else if (auth) {
      throw AuthRequiredException();
    }
    return headers;
  }

  static dynamic _decode(http.Response r) {
    final body = r.body.isEmpty ? null : jsonDecode(utf8.decode(r.bodyBytes));
    if (r.statusCode == 401) throw AuthRequiredException();
    if (r.statusCode >= 400) {
      String msg = 'Request failed (${r.statusCode})';
      if (body is Map) {
        final v = body['error'] ?? body['detail'] ?? body['message'] ?? body['non_field_errors'];
        if (v is List && v.isNotEmpty) {
          msg = v.first.toString();
        } else if (v != null) {
          msg = v.toString();
        }
      }
      throw ApiException(msg);
    }
    return body;
  }

  /// Exchange the stored refresh token for a new access token.
  /// Returns false (and clears the session) if the refresh token is invalid.
  static Future<bool> refreshSession() async {
    final prefs = await SharedPreferences.getInstance();
    final refresh = prefs.getString('refresh_token');
    if (refresh == null) return false;
    try {
      final r = await http.post(Uri.parse('$base/token/refresh/'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'refresh': refresh}));
      if (r.statusCode == 200) {
        final data = jsonDecode(r.body);
        await prefs.setString('access_token', data['access']);
        if (data['refresh'] != null) await prefs.setString('refresh_token', data['refresh']);
        return true;
      }
      if (r.statusCode == 401 || r.statusCode == 400) {
        for (final k in ['access_token', 'refresh_token', 'user_data', 'username', 'email']) {
          await prefs.remove(k);
        }
      }
    } catch (_) {}
    return false;
  }

  /// Send a request; on 401 refresh the access token once and retry.
  static Future<dynamic> _send(
      Future<http.Response> Function(Map<String, String> headers) call,
      {bool auth = false}) async {
    var r = await call(await _headers(auth: auth));
    if (r.statusCode == 401 && await refreshSession()) {
      r = await call(await _headers(auth: auth));
    }
    return _decode(r);
  }

  static Future<dynamic> get(String path, {bool auth = false, Map<String, String>? query}) {
    final uri = Uri.parse('$base$path').replace(queryParameters: query);
    return _send((h) => http.get(uri, headers: h), auth: auth);
  }

  static Future<dynamic> post(String path, Map<String, dynamic> body, {bool auth = true}) {
    return _send((h) => http.post(Uri.parse('$base$path'), headers: h, body: jsonEncode(body)),
        auth: auth);
  }

  static Future<dynamic> put(String path, Map<String, dynamic> body) {
    return _send((h) => http.put(Uri.parse('$base$path'), headers: h, body: jsonEncode(body)),
        auth: true);
  }

  // ---- convenience wrappers -------------------------------------------------
  static Future<List<dynamic>> trips({String? date}) async =>
      (await get('/trips/', query: date == null ? null : {'date': date})) as List<dynamic>;

  static Future<Map<String, dynamic>> tripDetails(int id) async =>
      (await get('/trips/$id/')) as Map<String, dynamic>;

  static Future<List<dynamic>> createBookings(int tripId, List<String> seats) async =>
      (await post('/bookings/create/', {'trip': tripId, 'seat_numbers': seats}))['bookings'];

  static Future<List<dynamic>> pay(List<int> ids, String method, String phone) async =>
      (await post('/bookings/pay/', {'booking_ids': ids, 'method': method, 'phone': phone}))['bookings'];

  static Future<List<dynamic>> myBookings() async {
    final data = await get('/bookings/', auth: true, query: {'page_size': '100'});
    return data is Map ? (data['results'] as List<dynamic>) : data as List<dynamic>;
  }

  static Future<void> cancelBooking(int id) => post('/bookings/$id/cancel/', {});

  static Future<Map<String, dynamic>> profile() async =>
      (await get('/profile/', auth: true))['profile'];

  static Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async =>
      (await put('/profile/update/', data))['profile'];

  static Future<Map<String, dynamic>> mapData() async =>
      (await get('/map/')) as Map<String, dynamic>;

  static Future<List<dynamic>> notifications() async =>
      (await get('/notifications/'))['notifications'];
}
