import 'package:flutter/material.dart';

class NotificationScreen extends StatelessWidget {

const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Notifications', style: TextStyle(color: Colors.white),),
      backgroundColor: Colors.blue.shade900,),
      body: Center(
        child: Text('Notification Screen',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
      )
    );
  }
}
