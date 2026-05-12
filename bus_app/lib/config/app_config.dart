class AppConfig {
  static const String baseUrl = String.fromEnvironment(
    'BOOKUTU_API_URL',
    defaultValue: 'http://10.0.2.2:4000',
  );
  static const String apiUrl = '$baseUrl/api/v1';
  
  // API Endpoints
  static const String tripsEndpoint = '$apiUrl/trips';
  static const String advertsEndpoint = '$apiUrl/adverts';
  static const String registerEndpoint = '$apiUrl/auth/register';
  static const String loginEndpoint = '$apiUrl/auth/login';
  static const String refreshEndpoint = '$apiUrl/auth/refresh';
  static const String meEndpoint = '$apiUrl/auth/me';
  static const String bookingsEndpoint = '$apiUrl/bookings';
  
  // Helper method to get trip seats endpoint
  static String getTripSeatsEndpoint(String tripId) => '$apiUrl/trips/$tripId/seats';
}
