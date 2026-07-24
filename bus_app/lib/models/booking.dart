class Booking {
  final List<int> seatNumbers;
  final String passengerName;
  final double totalAmount;
  final String status;
  final String? bookingReference;

  Booking({
    required this.seatNumbers,
    required this.passengerName,
    required this.totalAmount,
    required this.status,
    this.bookingReference,
  });

  factory Booking.preview({
    required List<int> seatNumbers,
    required String passengerName,
    required double seatPrice,
  }) {
    return Booking(
      seatNumbers: seatNumbers,
      passengerName: passengerName,
      totalAmount: seatNumbers.length * seatPrice,
      status: 'PREVIEW',
    );
  }

  factory Booking.fromJson(Map<String, dynamic> json) {
    return Booking(
      seatNumbers: List<int>.from(json['seat_numbers'] ?? []),
      passengerName: json['passenger_name']?.toString() ?? 'N/A',
      totalAmount: (json['total_amount'] as num?)?.toDouble() ?? 0,
      status: json['status']?.toString() ?? 'N/A',
      bookingReference: json['booking_reference']?.toString(),
    );
  }

  Booking copyWith({String? status, String? bookingReference}) {
    return Booking(
      seatNumbers: seatNumbers,
      passengerName: passengerName,
      totalAmount: totalAmount,
      status: status ?? this.status,
      bookingReference: bookingReference ?? this.bookingReference,
    );
  }

  Map<String, dynamic> toJson() => {
        'seat_numbers': seatNumbers,
        'passenger_name': passengerName,
        'total_amount': totalAmount,
        'status': status,
        if (bookingReference != null) 'booking_reference': bookingReference,
      };
}
