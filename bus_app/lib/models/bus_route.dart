class LatLngPoint {
  final double lat;
  final double lng;

  const LatLngPoint(this.lat, this.lng);
}

class BusRoute {
  final String name;
  final List<LatLngPoint> points;

  const BusRoute({required this.name, required this.points});
}
