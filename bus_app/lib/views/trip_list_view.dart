import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/trip_list_controller.dart';
import '../widgets/trip_card.dart';
import 'seat_selection_view.dart';

class BusListScreen extends StatelessWidget {
  const BusListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<TripListController>(
      create: (_) => TripListController(),
      child: const _TripListView(),
    );
  }
}

class _TripListView extends StatefulWidget {
  const _TripListView();

  @override
  State<_TripListView> createState() => _TripListViewState();
}

class _TripListViewState extends State<_TripListView> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadTrips());
  }

  Future<void> _loadTrips() async {
    final controller = context.read<TripListController>();
    await controller.loadTrips();
    if (!mounted) return;
    if (controller.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(controller.errorMessage!)),
      );
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<TripListController>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus List', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60.0),
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              onChanged: controller.updateSearch,
              decoration: InputDecoration(
                hintText: 'Search by route...',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide.none,
                ),
                prefixIcon: const Icon(Icons.search),
              ),
            ),
          ),
        ),
      ),
      body: controller.isLoading
          ? const Center(child: CircularProgressIndicator())
          : controller.filteredTrips.isEmpty
              ? const Center(child: Text("No trips available yet"))
              : GridView.builder(
                  padding: const EdgeInsets.all(12),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 0.7,
                  ),
                  itemCount: controller.filteredTrips.length,
                  itemBuilder: (context, index) {
                    final trip = controller.filteredTrips[index];
                    return TripCard(
                      trip: trip,
                      onBookNow: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => SeatSelectionScreen(trip: trip)),
                        );
                      },
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Feature coming soon!")),
          );
        },
        backgroundColor: Colors.blue.shade900,
        label: const Text("Book for later", style: TextStyle(color: Colors.white)),
        icon: const Icon(Icons.schedule, color: Colors.white),
      ),
    );
  }
}
