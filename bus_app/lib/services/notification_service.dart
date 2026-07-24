import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/booking.dart';
import '../models/saved_ticket.dart';
import '../models/trip.dart';

class NotificationService {
  static const String _ticketsKey = 'saved_tickets';

  static Future<void> saveTicket({
    required Booking bookingData,
    required Trip tripData,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    final ticket = SavedTicket(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: 'Booking Confirmed',
      message: 'Your ticket for ${tripData.routeName} has been confirmed',
      timestamp: DateTime.now().toIso8601String(),
      type: 'ticket',
      bookingData: bookingData,
      tripData: tripData,
    );

    final tickets = prefs.getStringList(_ticketsKey) ?? [];
    tickets.insert(0, jsonEncode(ticket.toJson())); // Add to beginning

    await prefs.setStringList(_ticketsKey, tickets);
  }

  static Future<List<SavedTicket>> getTickets() async {
    final prefs = await SharedPreferences.getInstance();
    final ticketStrings = prefs.getStringList(_ticketsKey) ?? [];

    return ticketStrings
        .map((raw) => SavedTicket.fromJson(jsonDecode(raw) as Map<String, dynamic>))
        .toList();
  }

  static Future<void> clearTickets() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_ticketsKey);
  }
}
