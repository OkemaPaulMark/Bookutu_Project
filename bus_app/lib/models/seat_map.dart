class SeatMap {
  final int busCapacity;
  final List<int> bookedSeats;
  final double seatPrice;

  SeatMap({
    required this.busCapacity,
    required this.bookedSeats,
    required this.seatPrice,
  });

  factory SeatMap.fromJson(Map<String, dynamic> json) {
    return SeatMap(
      busCapacity: json['bus_capacity'] ?? 40,
      bookedSeats: List<int>.from(json['booked_seats'] ?? []),
      seatPrice: (json['seat_price'] as num?)?.toDouble() ?? 50000.0,
    );
  }

  factory SeatMap.defaults() => SeatMap(busCapacity: 40, bookedSeats: [], seatPrice: 50000.0);
}
