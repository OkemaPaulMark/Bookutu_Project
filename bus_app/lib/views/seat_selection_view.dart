import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/seat_selection_controller.dart';
import '../models/trip.dart';
import '../widgets/seat_tile.dart';
import 'ticket_view.dart';

class SeatSelectionScreen extends StatelessWidget {
  final Trip trip;

  const SeatSelectionScreen({super.key, required this.trip});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<SeatSelectionController>(
      create: (_) => SeatSelectionController(),
      child: _SeatSelectionView(trip: trip),
    );
  }
}

class _SeatSelectionView extends StatefulWidget {
  final Trip trip;

  const _SeatSelectionView({required this.trip});

  @override
  State<_SeatSelectionView> createState() => _SeatSelectionViewState();
}

class _SeatSelectionViewState extends State<_SeatSelectionView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadSeatMap());
  }

  Future<void> _loadSeatMap() async {
    final controller = context.read<SeatSelectionController>();
    await controller.loadSeatMap(widget.trip.id);
    if (!mounted) return;
    if (controller.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(controller.errorMessage!)),
      );
    }
  }

  Color _colorFor(SeatStatus status) {
    switch (status) {
      case SeatStatus.booked:
        return Colors.red;
      case SeatStatus.selected:
        return Colors.yellow;
      case SeatStatus.available:
        return Colors.green;
    }
  }

  Future<void> _viewTicket(SeatSelectionController controller) async {
    if (controller.selectedSeats.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one seat')),
      );
      return;
    }

    final preview = await controller.buildPreview();
    if (!mounted) return;
    if (preview == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(controller.errorMessage ?? 'Unable to prepare booking, please try again')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TicketScreen(
          trip: widget.trip,
          booking: preview,
          isPreview: true,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<SeatSelectionController>();

    if (controller.isLoading) {
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
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                SpecialSeatTile(label: 'DRIVER'),
                Icon(Icons.directions_bus, size: 40),
              ],
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: (controller.busCapacity / 4).ceil(),
                itemBuilder: (context, rowIndex) {
                  int seatNumber = rowIndex * 4 + 1;
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            if (seatNumber <= controller.busCapacity)
                              SeatTile(
                                seatNumber: seatNumber,
                                color: _colorFor(controller.statusFor(seatNumber)),
                                onTap: () => controller.toggleSeat(seatNumber),
                              ),
                            const SizedBox(width: 10),
                            if (seatNumber + 1 <= controller.busCapacity)
                              SeatTile(
                                seatNumber: seatNumber + 1,
                                color: _colorFor(controller.statusFor(seatNumber + 1)),
                                onTap: () => controller.toggleSeat(seatNumber + 1),
                              ),
                          ],
                        ),
                        const SizedBox(width: 40),
                        Row(
                          children: [
                            if (seatNumber + 2 <= controller.busCapacity)
                              SeatTile(
                                seatNumber: seatNumber + 2,
                                color: _colorFor(controller.statusFor(seatNumber + 2)),
                                onTap: () => controller.toggleSeat(seatNumber + 2),
                              ),
                            const SizedBox(width: 10),
                            if (seatNumber + 3 <= controller.busCapacity)
                              SeatTile(
                                seatNumber: seatNumber + 3,
                                color: _colorFor(controller.statusFor(seatNumber + 3)),
                                onTap: () => controller.toggleSeat(seatNumber + 3),
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
                Text('Selected: ${controller.selectedSeats.join(', ')}'),
                Text(
                  'Total: UGX ${(controller.selectedSeats.length * controller.seatPrice).toStringAsFixed(0)}',
                ),
              ],
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
                backgroundColor: Colors.blue.shade900,
              ),
              onPressed: controller.selectedSeats.isEmpty ? null : () => _viewTicket(controller),
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
