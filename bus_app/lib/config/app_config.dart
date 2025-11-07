class AppConfig {
  // Azure production endpoint
  static const String baseUrl = 'http://4.222.184.37:8000';
  static const String apiUrl = '$baseUrl/api';
  
  // API Endpoints
  static const String tripsEndpoint = '$apiUrl/trips/';
  static const String advertsEndpoint = '$apiUrl/adverts/?all=true';
  static const String registerEndpoint = '$apiUrl/register/';
  static const String loginEndpoint = '$apiUrl/login/';
  static const String logoutEndpoint = '$apiUrl/logout/';
  static const String bookingsEndpoint = '$apiUrl/bookings/create/';
  
  // Helper method to get trip seats endpoint
  static String getTripSeatsEndpoint(String tripId) => '$apiUrl/trips/$tripId/seats/';
}