import 'dart:math';
import 'package:flutter/material.dart';
import 'package:bus_app/ticketui.dart';

class SeatSelectionScreen extends StatefulWidget {
  const SeatSelectionScreen({super.key, required Map<String, String> busData});

  @override
  State<SeatSelectionScreen> createState() => _SeatSelectionScreenState();
}

class _SeatSelectionScreenState extends State<SeatSelectionScreen> {
  final Set<int> selectedSeats = {};
  final List<int> soldSeats = List.generate(10, (_) => Random().nextInt(40) + 1);

  static const double seatPrice = 50000.0;

  Color _getSeatColor(int seatNumber) {
    if (soldSeats.contains(seatNumber)) {
      return Colors.red;
    } else if (selectedSeats.contains(seatNumber)) {
      return Colors.yellow;
    } else {
      return Colors.green;
    }
  }

  void _onSeatTap(int seatNumber) {
    if (soldSeats.contains(seatNumber)) return;
    setState(() {
      if (selectedSeats.contains(seatNumber)) {
        selectedSeats.remove(seatNumber);
      } else {
        selectedSeats.add(seatNumber);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blue.shade900,
        title: const Text('Select Your Seat', style: TextStyle(color: Colors.white),)),
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            // Legend Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _legendTile('Available', Colors.green),
                _legendTile('Sold', Colors.red),
                _legendTile('Selected', Colors.yellow),
              ],
            ),
            const SizedBox(height: 10),
            // Driver & Conductor
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                _SpecialSeat(label: 'STAFF'),
                Icon(Icons.bus_alert, size: 40),
              ],
            ),
            const SizedBox(height: 10),
            // Seats Layout
            Expanded(
              child: ListView.builder(
                itemCount: 10,
                itemBuilder: (context, rowIndex) {
                  int seatNumber = rowIndex * 4 + 1;
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            _Seat(
                              seatNumber: seatNumber,
                              color: _getSeatColor(seatNumber),
                              onTap: () => _onSeatTap(seatNumber),
                            ),
                            const SizedBox(width: 10),
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
                            _Seat(
                              seatNumber: seatNumber + 2,
                              color: _getSeatColor(seatNumber + 2),
                              onTap: () => _onSeatTap(seatNumber + 2),
                            ),
                            const SizedBox(width: 10),
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
                Text('Fare: Ugx ${(selectedSeats.length * seatPrice).toStringAsFixed(2)}'),
              ],
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
                backgroundColor: Colors.blue.shade900,
              ),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => TicketScreen()),
                );
              },
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
