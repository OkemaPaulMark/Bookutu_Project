import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/advert.dart';
import 'auth_service.dart';

const String _baseUrl = String.fromEnvironment(
  'BOOKUTU_API_URL',
  defaultValue: 'http://10.0.2.2:4000',
);
const String _apiUrl = '$_baseUrl/api/v1';
const String _advertsEndpoint = '$_apiUrl/adverts';

class AdvertService {
  final AuthService _authService;

  AdvertService({AuthService? authService}) : _authService = authService ?? AuthService();

  Future<List<Advert>> fetchAdverts() async {
    final token = await _authService.getAccessToken();
    final response = await http
        .get(
          Uri.parse(_advertsEndpoint),
          headers: {if (token != null) 'Authorization': 'Bearer $token'},
        )
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw Exception('Failed to load adverts: ${response.statusCode}');
    }

    final Map<String, dynamic> body = json.decode(response.body) as Map<String, dynamic>;
    final List<dynamic> data = body['data'] as List<dynamic>;
    return data.map((item) => Advert.fromJson(item as Map<String, dynamic>)).toList();
  }
}
