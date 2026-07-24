import 'package:flutter/foundation.dart';

class PastBooking {
  final String company;
  final String from;
  final String to;
  final String date;
  final String time;
  final String seats;
  final String status;

  const PastBooking({
    required this.company,
    required this.from,
    required this.to,
    required this.date,
    required this.time,
    required this.seats,
    required this.status,
  });
}

class BookingsController extends ChangeNotifier {
  // TODO: replace with GET /bookings once the backend exposes a list-bookings
  // endpoint for passengers — app_config.dart currently only has a
  // create-booking endpoint, so this list is illustrative sample data.
  final List<PastBooking> pastBookings = const [
    PastBooking(
      company: 'Global Coaches',
      from: 'Kampala',
      to: 'Mbarara',
      date: '2023-10-26',
      time: '06:00 AM',
      seats: 'A1, A2',
      status: 'Completed',
    ),
    PastBooking(
      company: 'YY Coaches',
      from: 'Jinja',
      to: 'Kampala',
      date: '2023-09-15',
      time: '07:00 AM',
      seats: 'B5',
      status: 'Completed',
    ),
    PastBooking(
      company: 'Friendship',
      from: 'Masaka',
      to: 'Kampala',
      date: '2023-08-01',
      time: '08:00 AM',
      seats: 'C3, C4, C5',
      status: 'Completed',
    ),
    PastBooking(
      company: 'Global Coaches',
      from: 'Gulu',
      to: 'Kampala',
      date: '2023-07-20',
      time: '01:00 PM',
      seats: 'D10',
      status: 'Completed',
    ),
  ];
}
