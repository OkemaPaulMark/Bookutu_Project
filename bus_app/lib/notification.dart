import 'package:flutter/material.dart';
import 'package:bus_app/theme.dart';
import 'package:intl/intl.dart';

import 'services/api_service.dart';

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  late Future<List<dynamic>> _future = ApiService.notifications();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications', style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() => _future = ApiService.notifications());
          await _future;
        },
        child: FutureBuilder<List<dynamic>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return ListView(children: [
                Padding(padding: const EdgeInsets.all(32), child: Text('${snap.error}'))
              ]);
            }
            final items = snap.data!;
            if (items.isEmpty) {
              return ListView(children: const [
                Padding(
                    padding: EdgeInsets.all(48),
                    child: Text('No notifications yet', textAlign: TextAlign.center))
              ]);
            }
            return ListView.separated(
              itemCount: items.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (_, i) {
                final n = items[i];
                final booking = n['type'] == 'booking';
                final when = DateTime.tryParse(n['created_at'] ?? '')?.toLocal();
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: booking
                        ? Colors.blue.withOpacity(0.18)
                        : (n['priority'] == 'high'
                            ? Colors.orange.withOpacity(0.2)
                            : Colors.green.withOpacity(0.2)),
                    child: Icon(booking ? Icons.confirmation_number : Icons.campaign,
                        color: context.brand),
                  ),
                  title: Text(n['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(n['message'] ?? ''),
                  trailing: when == null
                      ? null
                      : Text(DateFormat('d MMM').format(when),
                          style: const TextStyle(fontSize: 12, color: Colors.grey)),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
