class PassengerBooking {
  final String id;
  final String? bookingReference;
  final String companyName;
  final String originCity;
  final String destinationCity;
  final String departureDate;
  final String departureTime;
  final String busRegistration;
  final String seatLabel;
  final double totalAmount;
  final String status;

  PassengerBooking({
    required this.id,
    required this.bookingReference,
    required this.companyName,
    required this.originCity,
    required this.destinationCity,
    required this.departureDate,
    required this.departureTime,
    required this.busRegistration,
    required this.seatLabel,
    required this.totalAmount,
    required this.status,
  });

  factory PassengerBooking.fromJson(Map<String, dynamic> json) {
    final trip = json['trip'] as Map<String, dynamic>?;
    final route = trip?['route'] as Map<String, dynamic>?;
    final bus = trip?['bus'] as Map<String, dynamic>?;
    final company = trip?['company'] as Map<String, dynamic>?;
    final seat = json['seat'] as Map<String, dynamic>?;

    return PassengerBooking(
      id: json['id'].toString(),
      bookingReference: json['bookingReference']?.toString(),
      companyName: company?['name']?.toString() ?? 'N/A',
      originCity: route?['originCity']?.toString() ?? 'N/A',
      destinationCity: route?['destinationCity']?.toString() ?? 'N/A',
      departureDate: trip?['departureDate']?.toString() ?? 'N/A',
      departureTime: trip?['departureTime']?.toString() ?? '',
      busRegistration: bus?['licensePlate']?.toString() ?? 'N/A',
      seatLabel: seat?['seatNumber']?.toString() ?? 'N/A',
      totalAmount: (json['totalAmount'] as num?)?.toDouble() ?? 0,
      status: json['status']?.toString() ?? 'N/A',
    );
  }
}
