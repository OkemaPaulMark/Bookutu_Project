import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:bus_app/services/api_service.dart';
import 'seats_page.dart';

class BusListScreen extends StatefulWidget {
  const BusListScreen({super.key});

  @override
  State<BusListScreen> createState() => _BusListScreenState();
}

class _BusListScreenState extends State<BusListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchText = '';
  final ApiService _apiService = ApiService();
  String? _authToken;

  List<dynamic> _routes = [];
  List<dynamic> _trips = [];
  bool _isLoading = true;
  String? _selectedRouteId;
  DateTime? _selectedDate;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchText = _searchController.text;
      });
    });
    _loadAuthTokenAndFetchRoutes();
  }

  Future<void> _loadAuthTokenAndFetchRoutes() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('authToken');
    if (_authToken != null) {
      await _fetchRoutes();
    } else {
      // Handle case where token is not available, e.g., navigate to login
      print('Auth token not found. Please log in.');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _fetchRoutes() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final routes = await _apiService.fetchRoutes(_authToken!);
      setState(() {
        _routes = routes;
        _isLoading = false;
      });
    } catch (e) {
      print('Error fetching routes: $e');
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load routes: $e')),
      );
    }
  }

  Future<void> _fetchTrips(int routeId, DateTime departureDate) async {
    setState(() {
      _isLoading = true;
      _trips = []; // Clear previous trips
    });
    try {
      final formattedDate = departureDate.toIso8601String().split('T')[0];
      final trips = await _apiService.fetchTrips(_authToken!, routeId, formattedDate);
      setState(() {
        _trips = trips;
        _isLoading = false;
      });
    } catch (e) {
      print('Error fetching trips: $e');
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load trips: $e')),
      );
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<dynamic> get filteredTrips {
    if (_searchText.isEmpty) {
      return _trips;
    } else {
      return _trips.where((trip) {
        final routeName = trip['route_display']?.toLowerCase() ?? ''; // Use route_display from backend
        final busRegistration = trip['bus_registration']?.toLowerCase() ?? '';
        return routeName.contains(_searchText.toLowerCase()) ||
               busRegistration.contains(_searchText.toLowerCase());
      }).toList();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bus List', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue.shade900,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(120.0), // Increased height for dropdowns
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              children: [
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Search by route or bus...',
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide.none,
                    ),
                    prefixIcon: const Icon(Icons.search),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        decoration: InputDecoration(
                          hintText: 'Select Route',
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8.0),
                            borderSide: BorderSide.none,
                          ),
                        ),
                        value: _selectedRouteId,
                        items: _routes.map<DropdownMenuItem<String>>((route) {
                          return DropdownMenuItem<String>(
                            value: route['id'].toString(),
                            child: Text(route['route_display']),
                          );
                        }).toList(),
                        onChanged: (String? newValue) {
                          setState(() {
                            _selectedRouteId = newValue;
                            // Optionally fetch trips immediately if date is also selected
                            if (_selectedRouteId != null && _selectedDate != null) {
                              _fetchTrips(int.parse(_selectedRouteId!), _selectedDate!);
                            }
                          });
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: InkWell(
                        onTap: () async {
                          final DateTime? picked = await showDatePicker(
                            context: context,
                            initialDate: _selectedDate ?? DateTime.now(),
                            firstDate: DateTime.now(),
                            lastDate: DateTime.now().add(const Duration(days: 365)),
                          );
                          if (picked != null && picked != _selectedDate) {
                            setState(() {
                              _selectedDate = picked;
                              // Optionally fetch trips immediately if route is also selected
                              if (_selectedRouteId != null && _selectedDate != null) {
                                _fetchTrips(int.parse(_selectedRouteId!), _selectedDate!);
                              }
                            });
                          }
                        },
                        child: InputDecorator(
                          decoration: InputDecoration(
                            hintText: 'Select Date',
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8.0),
                              borderSide: BorderSide.none,
                            ),
                            suffixIcon: const Icon(Icons.calendar_today),
                          ),
                          child: Text(
                            _selectedDate == null
                                ? 'Select Date'
                                : '${_selectedDate!.toLocal()}'.split(' ')[0],
                            style: TextStyle(
                              color: _selectedDate == null ? Colors.grey[700] : Colors.black,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : filteredTrips.isEmpty
                ? const Center(child: Text("No trips found for the selected route and date."))
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: filteredTrips.length,
                    itemBuilder: (context, index) {
                      final trip = filteredTrips[index];
                      return TripCard(trip: trip, authToken: _authToken!);
                    },
                  ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text("Feature coming soon!",
                    style: TextStyle(color: Colors.white))),
          );
        },
        backgroundColor: Colors.blue.shade900,
        label:
            const Text("Book for later", style: TextStyle(color: Colors.white)),
        icon: const Icon(Icons.schedule, color: Colors.white),
      ),
    );
  }
}

class TripCard extends StatelessWidget {
  final Map<String, dynamic> trip;
  final String authToken;

  const TripCard({super.key, required this.trip, required this.authToken});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "${trip['route_display']}", // Use route_display from backend
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Departure: ${trip['departure_time']}"),
                Text("Arrival: ${trip['arrival_time']}"),
              ],
            ),
            const SizedBox(height: 4),
            Text("Bus: ${trip['bus_registration']}"),
            Text("Driver: ${trip['driver_name'] ?? 'N/A'}"),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Available Seats: ${trip['available_seats']}",
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                Text("Fare: UGX ${trip['base_fare']}",
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, color: Colors.green)),
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => SeatSelectionScreen(
                        tripId: trip['id'],
                        busRegistration: trip['bus_registration'],
                        totalSeats: trip['total_seats'],
                        authToken: authToken,
                      ),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue.shade900,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: const Text(
                  "Select Seats",
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
