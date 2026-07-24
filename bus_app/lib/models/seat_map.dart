class SeatInfo {
  final int seatNumber;
  final String seatId;
  final String label;
  final bool isWindow;
  final bool isAisle;
  final bool isBooked;

  SeatInfo({
    required this.seatNumber,
    required this.seatId,
    required this.label,
    required this.isWindow,
    required this.isAisle,
    required this.isBooked,
  });

  factory SeatInfo.fromJson(Map<String, dynamic> json) {
    return SeatInfo(
      seatNumber: (json['seatNumber'] as num).toInt(),
      seatId: json['seatId'].toString(),
      label: json['label']?.toString() ?? '',
      isWindow: json['isWindow'] as bool? ?? false,
      isAisle: json['isAisle'] as bool? ?? false,
      isBooked: json['status'] == 'BOOKED',
    );
  }
}

class SeatMap {
  final int busCapacity;
  final List<int> bookedSeats;
  final double seatPrice;
  final List<SeatInfo> seats;

  SeatMap({
    required this.busCapacity,
    required this.bookedSeats,
    required this.seatPrice,
    required this.seats,
  });

  String? seatIdFor(int seatNumber) {
    for (final seat in seats) {
      if (seat.seatNumber == seatNumber) return seat.seatId;
    }
    return null;
  }

  String? seatLabelFor(int seatNumber) {
    for (final seat in seats) {
      if (seat.seatNumber == seatNumber) return seat.label;
    }
    return null;
  }

  factory SeatMap.fromJson(Map<String, dynamic> json) {
    final data = (json['data'] as Map<String, dynamic>?) ?? json;
    final seatList = (data['seats'] as List<dynamic>? ?? [])
        .map((item) => SeatInfo.fromJson(item as Map<String, dynamic>))
        .toList();

    return SeatMap(
      busCapacity: (data['busCapacity'] as num?)?.toInt() ?? 40,
      bookedSeats: List<int>.from(data['bookedSeats'] ?? []),
      seatPrice: (data['seatPrice'] as num?)?.toDouble() ?? 50000.0,
      seats: seatList,
    );
  }

  factory SeatMap.defaults() => SeatMap(busCapacity: 40, bookedSeats: [], seatPrice: 50000.0, seats: []);
}
