# Mobile API Testing Guide

## Quick Start

### 1. Create Test Passenger User

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create test passenger
passenger = User.objects.create_user(
    email="passenger@test.com",
    password="test123",
    first_name="Test",
    last_name="Passenger",
    phone_number="0700111222",
    user_type=''  # Empty for passengers (not staff)
)
print(f"Created passenger: {passenger.email}")
```

### 2. Test Registration Endpoint

```bash
# PowerShell
$body = @{
    email = "newpassenger@test.com"
    password = "test123"
    first_name = "New"
    last_name = "Passenger"
    phone_number = "0700333444"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/mobile/auth/register/" -Method POST -Body $body -ContentType "application/json"
```

### 3. Test Login Endpoint

```bash
# PowerShell
$body = @{
    email = "passenger@test.com"
    password = "test123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/mobile/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = ($response.Content | ConvertFrom-Json).access
Write-Host "JWT Token: $token"
```

### 4. Test Booking Endpoint

```bash
# PowerShell (replace TOKEN with actual token from step 3)
$token = "your_jwt_token_here"
$headers = @{
    "Authorization" = "Bearer $token"
}
$body = @{
    trip = 1
    seat = 1
    passenger_name = "Test Passenger"
    passenger_phone = "0700111222"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/mobile/bookings/create/" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

## All Mobile API Endpoints

### Authentication (No Auth Required)

- `POST /api/mobile/auth/register/` - Register new passenger
- `POST /api/mobile/auth/login/` - Login and get JWT token
- `POST /api/mobile/auth/token/refresh/` - Refresh JWT token

### Trip Search (No Auth Required)

- `POST /api/mobile/trips/search/` - Search available trips
- `GET /api/mobile/trips/{id}/` - Get trip details with seat map
- `GET /api/mobile/routes/popular/` - Get popular routes

### Bookings (Auth Required)

- `POST /api/mobile/bookings/create/` - Create new booking
- `GET /api/mobile/bookings/` - List user's bookings
- `GET /api/mobile/bookings/{id}/` - Get booking details
- `POST /api/mobile/bookings/{id}/cancel/` - Cancel booking

### User Profile (Auth Required)

- `GET /api/mobile/profile/` - Get user profile
- `PUT /api/mobile/profile/` - Update user profile

### Notifications (Auth Required)

- `GET /api/mobile/notifications/` - Get user notifications
- `POST /api/mobile/notifications/{id}/mark-read/` - Mark notification as read

### Device Registration (Auth Required)

- `POST /api/mobile/devices/register/` - Register device for push notifications

## Running Tests

```bash
# Run all mobile API tests
python manage.py test api.tests.test_mobile_booking -v 2

# Run specific test
python manage.py test api.tests.test_mobile_booking.MobileBookingAPITests.test_create_booking_success -v 2
```

## Common Issues

### Issue: "Company staff must be assigned to a company"

**Solution**: Make sure passenger users have `user_type=''` (empty string), not 'COMPANY_STAFF'

### Issue: "Seat is already booked"

**Solution**: Check if the seat is already reserved for the trip. Use a different seat or cancel the existing booking.

### Issue: "Authentication credentials were not provided"

**Solution**: Include JWT token in Authorization header: `Authorization: Bearer <token>`

### Issue: "Trip is not bookable"

**Solution**: Make sure the trip status is 'SCHEDULED' and departure is in the future.

## Database Setup for Testing

```python
# Run in Django shell (python manage.py shell)
from companies.models import Company, Bus
from trips.models import Route, Trip
from django.utils import timezone
from datetime import timedelta

# Create test company
company = Company.objects.create(
    name="Test Bus Company",
    slug="test-bus-co",
    email="test@busco.com",
    phone_number="0700000000",
    registration_number="REG123",
    license_number="LIC123"
)

# Create test bus (seats will be auto-generated)
bus = Bus.objects.create(
    company=company,
    license_plate="UAA123A",
    model="Isuzu",
    make="FTR",
    year=2020,
    total_seats=40,  # Will create 40 seats automatically
    status="ACTIVE"
)

# Create test route
route = Route.objects.create(
    company=company,
    name="Kampala - Gulu",
    origin_city="Kampala",
    destination_city="Gulu",
    distance_km=350,
    estimated_duration_hours=6.0,
    base_fare=20000
)

# Create test trip (tomorrow)
tomorrow = timezone.now() + timedelta(days=1)
trip = Trip.objects.create(
    company=company,
    route=route,
    bus=bus,
    departure_date=tomorrow.date(),
    departure_time=tomorrow.time(),
    base_fare=20000,
    available_seats=bus.total_seats,
    status="SCHEDULED"
)

print(f"Created trip #{trip.id} with {bus.seats.count()} seats")
```

## Notes

- Passenger users have `user_type=''` (empty) - they are NOT company staff
- Company staff users have `user_type='COMPANY_STAFF'` and must have a company
- All booking endpoints require JWT authentication
- Seats are auto-generated when a bus is created (2-2 layout: A, B | aisle | C, D)
