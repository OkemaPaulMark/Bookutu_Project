import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class NotificationService {
  static const String _ticketsKey = 'saved_tickets';

  static Future<void> saveTicket({
    required Map<String, dynamic> bookingData,
    required Map<String, String> tripData,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    
    final ticket = {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'title': 'Booking Confirmed',
      'message': 'Your ticket for ${tripData['route_name']} has been confirmed',
      'timestamp': DateTime.now().toIso8601String(),
      'type': 'ticket',
      'bookingData': bookingData,
      'tripData': tripData,
    };

    List<String> tickets = prefs.getStringList(_ticketsKey) ?? [];
    tickets.insert(0, jsonEncode(ticket)); // Add to beginning
    
    await prefs.setStringList(_ticketsKey, tickets);
  }

  static Future<List<Map<String, dynamic>>> getTickets() async {
    final prefs = await SharedPreferences.getInstance();
    List<String> ticketStrings = prefs.getStringList(_ticketsKey) ?? [];
    
    return ticketStrings.map((ticketString) {
      return Map<String, dynamic>.from(jsonDecode(ticketString));
    }).toList();
  }

  static Future<void> clearTickets() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_ticketsKey);
  }
}