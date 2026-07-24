import 'package:flutter/foundation.dart';

import '../models/advert.dart';
import '../services/advert_service.dart';
import '../services/notification_service.dart';

class HomeController extends ChangeNotifier {
  final AdvertService _advertService;

  HomeController({AdvertService? advertService}) : _advertService = advertService ?? AdvertService();

  List<Advert> _adverts = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<Advert> get adverts => _adverts;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> loadAdverts() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _adverts = await _advertService.fetchAdverts();
    } catch (e) {
      _errorMessage = 'Failed to connect to server: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<int> getNotificationCount() async {
    final tickets = await NotificationService.getTickets();
    return tickets.length;
  }
}
