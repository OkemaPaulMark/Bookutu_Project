import 'booking.dart';
import 'trip.dart';

class SavedTicket {
  final String id;
  final String title;
  final String message;
  final String timestamp;
  final String type;
  final Booking bookingData;
  final Trip tripData;

  SavedTicket({
    required this.id,
    required this.title,
    required this.message,
    required this.timestamp,
    required this.type,
    required this.bookingData,
    required this.tripData,
  });

  factory SavedTicket.fromJson(Map<String, dynamic> json) {
    return SavedTicket(
      id: json['id'].toString(),
      title: json['title']?.toString() ?? 'Notification',
      message: json['message']?.toString() ?? '',
      timestamp: json['timestamp']?.toString() ?? '',
      type: json['type']?.toString() ?? '',
      bookingData: Booking.fromJson(Map<String, dynamic>.from(json['bookingData'] ?? {})),
      tripData: Trip.fromJson(Map<String, dynamic>.from(json['tripData'] ?? {})),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'message': message,
        'timestamp': timestamp,
        'type': type,
        'bookingData': bookingData.toJson(),
        'tripData': tripData.toJson(),
      };
}
