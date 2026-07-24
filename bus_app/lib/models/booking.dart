class Booking {
  final List<int> seatNumbers;
  final List<String> seatLabels;
  final String passengerName;
  final String passengerPhone;
  final double totalAmount;
  final String status;
  final String? bookingReference;
  // Real BusSeat ids, same order as seatNumbers. Only populated on a preview
  // (before the seats are actually booked) so confirmBooking() knows which
  // real seat to submit for each selected seat number.
  final List<String>? seatIds;

  Booking({
    required this.seatNumbers,
    required this.seatLabels,
    required this.passengerName,
    required this.passengerPhone,
    required this.totalAmount,
    required this.status,
    this.bookingReference,
    this.seatIds,
  });

  factory Booking.preview({
    required List<int> seatNumbers,
    required List<String> seatIds,
    required List<String> seatLabels,
    required String passengerName,
    required String passengerPhone,
    required double seatPrice,
  }) {
    return Booking(
      seatNumbers: seatNumbers,
      seatIds: seatIds,
      seatLabels: seatLabels,
      passengerName: passengerName,
      passengerPhone: passengerPhone,
      totalAmount: seatNumbers.length * seatPrice,
      status: 'PREVIEW',
    );
  }

  // Round-trips a Booking previously saved locally via toJson() (notifications/saved tickets).
  factory Booking.fromJson(Map<String, dynamic> json) {
    return Booking(
      seatNumbers: List<int>.from(json['seatNumbers'] ?? []),
      seatLabels: List<String>.from(json['seatLabels'] ?? []),
      passengerName: json['passengerName']?.toString() ?? 'N/A',
      passengerPhone: json['passengerPhone']?.toString() ?? '',
      totalAmount: (json['totalAmount'] as num?)?.toDouble() ?? 0,
      status: json['status']?.toString() ?? 'N/A',
      bookingReference: json['bookingReference']?.toString(),
    );
  }

  // Parses one confirmed booking (one seat) as returned by POST /bookings,
  // which is wrapped in a {"data": {...}} envelope with camelCase keys.
  factory Booking.fromBookingResponse(Map<String, dynamic> body, {required int seatNumber}) {
    final data = (body['data'] as Map<String, dynamic>?) ?? body;
    final seat = data['seat'] as Map<String, dynamic>?;
    return Booking(
      seatNumbers: [seatNumber],
      seatLabels: [seat?['seatNumber']?.toString() ?? '$seatNumber'],
      passengerName: data['passengerName']?.toString() ?? 'N/A',
      passengerPhone: data['passengerPhone']?.toString() ?? '',
      totalAmount: (data['totalAmount'] as num?)?.toDouble() ?? 0,
      status: data['status']?.toString() ?? 'N/A',
      bookingReference: data['bookingReference']?.toString(),
    );
  }

  // Combines multiple single-seat bookings (one purchase spanning several
  // seats) into a single ticket-shaped Booking for display.
  static Booking combine(List<Booking> bookings) {
    final pairs = <MapEntry<int, String>>[];
    for (final b in bookings) {
      for (var i = 0; i < b.seatNumbers.length; i++) {
        pairs.add(MapEntry(b.seatNumbers[i], b.seatLabels[i]));
      }
    }
    pairs.sort((a, b) => a.key.compareTo(b.key));

    return Booking(
      seatNumbers: pairs.map((p) => p.key).toList(),
      seatLabels: pairs.map((p) => p.value).toList(),
      passengerName: bookings.first.passengerName,
      passengerPhone: bookings.first.passengerPhone,
      totalAmount: bookings.fold(0.0, (sum, b) => sum + b.totalAmount),
      status: bookings.every((b) => b.status == 'CONFIRMED') ? 'CONFIRMED' : bookings.first.status,
      bookingReference: bookings.map((b) => b.bookingReference).whereType<String>().join(', '),
    );
  }

  Booking copyWith({String? status, String? bookingReference}) {
    return Booking(
      seatNumbers: seatNumbers,
      seatLabels: seatLabels,
      passengerName: passengerName,
      passengerPhone: passengerPhone,
      totalAmount: totalAmount,
      status: status ?? this.status,
      bookingReference: bookingReference ?? this.bookingReference,
    );
  }

  Map<String, dynamic> toJson() => {
        'seatNumbers': seatNumbers,
        'seatLabels': seatLabels,
        'passengerName': passengerName,
        'passengerPhone': passengerPhone,
        'totalAmount': totalAmount,
        'status': status,
        if (bookingReference != null) 'bookingReference': bookingReference,
      };
}
