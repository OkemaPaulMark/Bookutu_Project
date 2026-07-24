class Trip {
  final String id;
  final String companyName;
  final String routeName;
  final String busRegistration;
  final String? driverName;
  final String departureDate;
  final String departureTime;
  final String arrivalTime;
  final num baseFare;
  final int availableSeats;
  final String status;

  Trip({
    required this.id,
    required this.companyName,
    required this.routeName,
    required this.busRegistration,
    this.driverName,
    required this.departureDate,
    required this.departureTime,
    required this.arrivalTime,
    required this.baseFare,
    required this.availableSeats,
    required this.status,
  });

  // Handles two shapes: Django's API response (nested route/bus/driver
  // objects) and this model's own toJson() output round-tripping back in
  // from local ticket storage (already-flat routeName/busRegistration).
  factory Trip.fromJson(Map<String, dynamic> json) {
    if (json.containsKey('routeName')) {
      return Trip(
        id: json['id'].toString(),
        companyName: json['companyName']?.toString() ?? 'N/A',
        routeName: json['routeName']?.toString() ?? 'N/A',
        busRegistration: json['busRegistration']?.toString() ?? 'N/A',
        driverName: json['driverName']?.toString(),
        departureDate: json['departureDate']?.toString() ?? 'N/A',
        departureTime: json['departureTime']?.toString() ?? '',
        arrivalTime: json['arrivalTime']?.toString() ?? '',
        baseFare: json['baseFare'] is num
            ? json['baseFare'] as num
            : num.tryParse(json['baseFare']?.toString() ?? '') ?? 0,
        availableSeats: (json['availableSeats'] as num?)?.toInt() ?? 0,
        status: json['status']?.toString() ?? 'SCHEDULED',
      );
    }

    final company = json['company'] as Map<String, dynamic>?;
    final route = json['route'] as Map<String, dynamic>?;
    final bus = json['bus'] as Map<String, dynamic>?;
    final driver = json['driver'] as Map<String, dynamic>?;

    final routeName = route != null
        ? '${route['originCity'] ?? ''} → ${route['destinationCity'] ?? ''}'
        : 'N/A';
    final driverName = driver != null
        ? '${driver['firstName'] ?? ''} ${driver['lastName'] ?? ''}'.trim()
        : null;

    return Trip(
      id: json['id'].toString(),
      companyName: company?['name']?.toString() ?? 'N/A',
      routeName: routeName,
      busRegistration: bus?['licensePlate']?.toString() ?? 'N/A',
      driverName: (driverName?.isEmpty ?? true) ? null : driverName,
      departureDate: json['departureDate']?.toString() ?? 'N/A',
      departureTime: json['departureTime']?.toString() ?? '',
      arrivalTime: json['arrivalTime']?.toString() ?? '',
      baseFare: json['baseFare'] is num
          ? json['baseFare'] as num
          : num.tryParse(json['baseFare']?.toString() ?? '') ?? 0,
      availableSeats: (json['availableSeats'] as num?)?.toInt() ?? 0,
      status: json['status']?.toString() ?? 'SCHEDULED',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'companyName': companyName,
        'routeName': routeName,
        'busRegistration': busRegistration,
        if (driverName != null) 'driverName': driverName,
        'departureDate': departureDate,
        'departureTime': departureTime,
        'arrivalTime': arrivalTime,
        'baseFare': baseFare,
        'availableSeats': availableSeats,
        'status': status,
      };
}
