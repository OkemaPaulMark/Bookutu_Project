import 'package:flutter/material.dart';

class SeatTile extends StatelessWidget {
  final int seatNumber;
  final Color color;
  final VoidCallback onTap;

  const SeatTile({super.key, required this.seatNumber, required this.color, required this.onTap});

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

class SpecialSeatTile extends StatelessWidget {
  final String label;

  const SpecialSeatTile({super.key, required this.label});

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
