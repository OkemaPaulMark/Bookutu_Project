import 'package:geolocator/geolocator.dart';

import '../models/bus_route.dart';
import '../models/bus_terminal.dart';

class LocationService {
  Future<LatLngPoint?> getCurrentPosition() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
      final position = await Geolocator.getCurrentPosition();
      return LatLngPoint(position.latitude, position.longitude);
    }

    return null;
  }

  List<BusTerminal> get busTerminals => const [
        // Central Region
        BusTerminal(name: 'Kampala Central Terminal', lat: 0.3152, lng: 32.5816),
        BusTerminal(name: 'Entebbe Terminal', lat: 0.0522, lng: 32.4634),
        BusTerminal(name: 'Mukono Terminal', lat: 0.3533, lng: 32.7574),

        // Eastern Region
        BusTerminal(name: 'Jinja Terminal', lat: 0.4244, lng: 33.2041),
        BusTerminal(name: 'Mbale Terminal', lat: 1.0827, lng: 34.1754),
        BusTerminal(name: 'Tororo Terminal', lat: 0.6928, lng: 34.1801),
        BusTerminal(name: 'Soroti Terminal', lat: 1.7147, lng: 33.6111),

        // Northern Region
        BusTerminal(name: 'Gulu Terminal', lat: 2.7796, lng: 32.2993),
        BusTerminal(name: 'Lira Terminal', lat: 2.2491, lng: 32.8998),
        BusTerminal(name: 'Kitgum Terminal', lat: 3.2781, lng: 32.8864),

        // Western Region
        BusTerminal(name: 'Mbarara Terminal', lat: -0.6107, lng: 30.6591),
        BusTerminal(name: 'Fort Portal Terminal', lat: 0.6712, lng: 30.2747),
        BusTerminal(name: 'Kasese Terminal', lat: 0.1833, lng: 30.0833),
        BusTerminal(name: 'Kabale Terminal', lat: -1.2481, lng: 29.9894),

        // West Nile Region
        BusTerminal(name: 'Arua Terminal', lat: 3.0197, lng: 30.9107),
        BusTerminal(name: 'Nebbi Terminal', lat: 2.4786, lng: 31.0889),
      ];

  List<BusRoute> get busRoutes => const [
        BusRoute(name: 'Kampala - Entebbe', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(0.0522, 32.4634),
        ]),
        BusRoute(name: 'Kampala - Jinja', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(0.4244, 33.2041),
        ]),
        BusRoute(name: 'Kampala - Mbale', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(0.4244, 33.2041),
          LatLngPoint(1.0827, 34.1754),
        ]),
        BusRoute(name: 'Kampala - Gulu', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(2.7796, 32.2993),
        ]),
        BusRoute(name: 'Kampala - Mbarara', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(-0.6107, 30.6591),
        ]),
        BusRoute(name: 'Kampala - Arua', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(2.7796, 32.2993),
          LatLngPoint(3.0197, 30.9107),
        ]),
        BusRoute(name: 'Kampala - Fort Portal', points: [
          LatLngPoint(0.3152, 32.5816),
          LatLngPoint(0.6712, 30.2747),
        ]),
      ];
}
