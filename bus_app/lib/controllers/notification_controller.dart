import 'package:flutter/foundation.dart';

import '../models/saved_ticket.dart';
import '../services/notification_service.dart';

class NotificationController extends ChangeNotifier {
  List<SavedTicket> _notifications = [];
  bool _isLoading = true;

  List<SavedTicket> get notifications => _notifications;
  bool get isLoading => _isLoading;

  Future<void> loadNotifications() async {
    _isLoading = true;
    notifyListeners();
    _notifications = await NotificationService.getTickets();
    _isLoading = false;
    notifyListeners();
  }
}
