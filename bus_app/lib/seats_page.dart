import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:bus_app/ticketui.dart';
import 'services/auth_service.dart';
import '../config/app_config.dart';

class SeatSelectionScreen extends StatefulWidget {
  final Map<String, String> busData;
  
  const SeatSelectionScreen({super.key, required this.busData});

  @override
  State<SeatSelectionScreen> createState() => _SeatSelectionScreenState();
}

class _SeatSelectionScreenState extends State<SeatSelectionScreen> {
  final Set<int> selectedSeats = {};
  List<int> bookedSeats = [];
  int busCapacity = 40;
  double seatPrice = 50000.0;
  bool isLoading = true;
  final AuthService _authService = AuthService();
  
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadSeatData();
  }

  Future<void> _loadSeatData() async {
    try {
      final tripId = widget.busData['id'] ?? '';
      final response = await http.get(
        Uri.parse(AppConfig.getTripSeatsEndpoint(tripId)),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          busCapacity = data['bus_capacity'] ?? 40;
          bookedSeats = List<int>.from(data['booked_seats'] ?? []);
          seatPrice = data['seat_price']?.toDouble() ?? 50000.0;
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading seats: $e')),
      );
    }
  }

  Color _getSeatColor(int seatNumber) {
    if (bookedSeats.contains(seatNumber)) {
      return Colors.red;
    } else if (selectedSeats.contains(seatNumber)) {
      return Colors.yellow;
    } else {
      return Colors.green;
    }
  }

  void _onSeatTap(int seatNumber) {
    if (bookedSeats.contains(seatNumber)) return;
    setState(() {
      if (selectedSeats.contains(seatNumber)) {
        selectedSeats.remove(seatNumber);
      } else {
        selectedSeats.add(seatNumber);
      }
    });
  }

  Future<void> _viewTicket() async {
    if (selectedSeats.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one seat')),
      );
      return;
    }

    final userData = await _authService.getUserData();
    
    // Create preview data without booking
    final previewData = {
      'seat_numbers': selectedSeats.toList(),
      'passenger_name': userData?['username'] ?? 'User',
      'total_amount': selectedSeats.length * seatPrice,
      'status': 'PREVIEW'
    };

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TicketScreen(
          bookingData: previewData,
          tripData: widget.busData,
          isPreview: true,
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.blue.shade900,
          title: const Text('Select Your Seat', style: TextStyle(color: Colors.white)),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blue.shade900,
        title: const Text('Select Your Seat', style: TextStyle(color: Colors.white)),
      ),
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _legendTile('Available', Colors.green),
                _legendTile('Booked', Colors.red),
                _legendTile('Selected', Colors.yellow),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                _SpecialSeat(label: 'DRIVER'),
                Icon(Icons.directions_bus, size: 40),
              ],
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: (busCapacity / 4).ceil(),
                itemBuilder: (context, rowIndex) {
                  int seatNumber = rowIndex * 4 + 1;
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            if (seatNumber <= busCapacity)
                              _Seat(
                                seatNumber: seatNumber,
                                color: _getSeatColor(seatNumber),
                                onTap: () => _onSeatTap(seatNumber),
                              ),
                            const SizedBox(width: 10),
                            if (seatNumber + 1 <= busCapacity)
                              _Seat(
                                seatNumber: seatNumber + 1,
                                color: _getSeatColor(seatNumber + 1),
                                onTap: () => _onSeatTap(seatNumber + 1),
                              ),
                          ],
                        ),
                        const SizedBox(width: 40),
                        Row(
                          children: [
                            if (seatNumber + 2 <= busCapacity)
                              _Seat(
                                seatNumber: seatNumber + 2,
                                color: _getSeatColor(seatNumber + 2),
                                onTap: () => _onSeatTap(seatNumber + 2),
                              ),
                            const SizedBox(width: 10),
                            if (seatNumber + 3 <= busCapacity)
                              _Seat(
                                seatNumber: seatNumber + 3,
                                color: _getSeatColor(seatNumber + 3),
                                onTap: () => _onSeatTap(seatNumber + 3),
                              ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 12),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Selected: ${selectedSeats.join(', ')}'),
                Text('Total: UGX ${(selectedSeats.length * seatPrice).toStringAsFixed(0)}'),
              ],
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
                backgroundColor: Colors.blue.shade900,
              ),
              onPressed: selectedSeats.isEmpty ? null : _viewTicket,
              child: const Text('View Ticket', style: TextStyle(fontSize: 18, color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _legendTile(String label, Color color) {
    return Row(
      children: [
        Container(width: 20, height: 20, color: color),
        const SizedBox(width: 6),
        Text(label),
      ],
    );
  }
}

class _Seat extends StatelessWidget {
  final int seatNumber;
  final Color color;
  final VoidCallback onTap;

  const _Seat({required this.seatNumber, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 60,
        height: 50,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Text(
            '$seatNumber',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }
}

class _SpecialSeat extends StatelessWidget {
  final String label;

  const _SpecialSeat({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 100,
      height: 55,
      decoration: BoxDecoration(
        color: Colors.blue.shade900,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Center(
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}