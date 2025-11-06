import 'dart:convert';
import 'package:http/http.dart' as http;

class NetworkTest {
  static const String baseUrl = 'http://10.10.132.24:8000';
  
  static Future<void> testConnection() async {
    print('=== Network Test Started ===');
    
    // Test 1: Basic connectivity
    try {
      print('Testing basic connectivity to $baseUrl...');
      final response = await http.get(Uri.parse(baseUrl)).timeout(const Duration(seconds: 5));
      print('Basic connection: ${response.statusCode}');
    } catch (e) {
      print('Basic connection failed: $e');
    }
    
    // Test 2: API endpoint
    try {
      print('Testing API endpoint...');
      final response = await http.get(Uri.parse('$baseUrl/api/')).timeout(const Duration(seconds: 5));
      print('API endpoint: ${response.statusCode}');
    } catch (e) {
      print('API endpoint failed: $e');
    }
    
    // Test 3: Adverts endpoint
    try {
      print('Testing adverts endpoint...');
      final response = await http.get(Uri.parse('$baseUrl/api/adverts/?all=true')).timeout(const Duration(seconds: 5));
      print('Adverts endpoint: ${response.statusCode}');
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Adverts data: ${data.length} items');
      }
    } catch (e) {
      print('Adverts endpoint failed: $e');
    }
    
    // Test 4: Trips endpoint
    try {
      print('Testing trips endpoint...');
      final response = await http.get(Uri.parse('$baseUrl/api/trips/')).timeout(const Duration(seconds: 5));
      print('Trips endpoint: ${response.statusCode}');
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Trips data: ${data.length} items');
      }
    } catch (e) {
      print('Trips endpoint failed: $e');
    }
    
    print('=== Network Test Completed ===');
  }
}