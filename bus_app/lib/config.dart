import 'package:flutter/foundation.dart' show kIsWeb;

/// Backend base URL.
///
/// - Override at build/run time: --dart-define=API_HOST=https://your-server
/// - Web builds without an override use the address the page was served from
///   (the hosted web app is served by the Django backend itself).
/// - Otherwise falls back to the dev machine's LAN IP.
const String _apiHostOverride = String.fromEnvironment('API_HOST');

final String apiHost = _apiHostOverride.isNotEmpty
    ? _apiHostOverride
    : (kIsWeb && Uri.base.host != 'localhost' && Uri.base.host != '127.0.0.1')
        ? Uri.base.origin
        : 'http://10.10.132.38:8000';
