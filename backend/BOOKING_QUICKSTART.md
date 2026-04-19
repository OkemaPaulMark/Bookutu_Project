# Bookutu Booking System - Quick Start Guide

## For Web Interface Users (Company Staff)

### Creating a Direct Booking

1. **Navigate to Bookings**

   ```
   Login → Company Dashboard → Bookings → Create Booking
   Or directly: http://localhost:8000/company/bookings/create/
   ```

2. **Step 1: Select Route & Trip**

   - Choose route (e.g., "Kampala → Gulu")
   - Pick departure date
   - Click on desired trip card
   - See fare displayed: **UGX 20,000** (base fare)

3. **Step 2: Select Seat**

   - View interactive bus layout
   - Available seats are **green**
   - Booked seats are **red** (cannot select)
   - Reserved seats are **yellow** (held by others)
   - Click an available seat
   - **Fare automatically updates!**
     - Base Fare: UGX 20,000
     - Seat Fee: UGX 5,000 (if premium seat)
     - **Total: UGX 25,000**

4. **Step 3: Passenger Details**

   - Enter passenger name (required)
   - Enter phone number (required)
   - Add email (optional)

5. **Step 4: Confirm**
   - Review all details
   - See final fare breakdown
   - Click "Confirm & Create Booking"
   - Get booking reference (e.g., BK20251019ABC123)

## For Mobile App Developers

### API Endpoint: Create Booking

```http
POST /api/mobile/bookings/create/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "trip": 5,
  "seat": 12,
  "passenger_name": "John Doe",
  "passenger_phone": "0700000000",
  "passenger_email": "john@example.com"
}
```

**Alternative (using seat number):**

```json
{
  "trip": 5,
  "seat_number": "12A",
  "passenger_name": "John Doe",
  "passenger_phone": "0700000000"
}
```

### Response (Success - 201)

```json
{
  "message": "Booking created successfully",
  "booking": {
    "id": 123,
    "booking_reference": "BK20251019ABC123",
    "status": "PENDING",
    "trip_info": {
      "company_name": "Swift Bus",
      "route": "Kampala → Gulu",
      "departure_time": "08:00:00",
      "arrival_time": "14:00:00",
      "departure_date": "2025-10-20",
      "bus_type": "LUXURY"
    },
    "seat_info": {
      "seat_number": "12A",
      "seat_type": "PREMIUM",
      "price": 25000.0
    },
    "total_amount": "25000.00",
    "payment_info": null,
    "created_at": "2025-10-19T10:30:00Z",
    "qr_code": "BOOKUTU:BK20251019ABC123:123"
  }
}
```

### Response (Error - 400)

```json
{
  "non_field_errors": ["Seat is already booked"]
}
```

```json
{
  "non_field_errors": ["Trip is not available for booking"]
}
```

## Getting Available Seats

### Web API (for web interface)

```http
GET /bookings/direct/trips/5/seats/
Authorization: Session (logged in)
```

### Response

```json
{
  "trip_id": 5,
  "bus_registration": "UAA123A",
  "total_seats": 40,
  "available_seats": 25,
  "seats": [
    {
      "id": 1,
      "seat_number": "1A",
      "row_number": 1,
      "seat_position": "LEFT",
      "seat_type": "REGULAR",
      "is_window": true,
      "is_aisle": false,
      "has_extra_legroom": false,
      "price_multiplier": 1.0,
      "status": "available",
      "price": 20000.0
    },
    {
      "id": 12,
      "seat_number": "12A",
      "row_number": 3,
      "seat_position": "LEFT",
      "seat_type": "PREMIUM",
      "is_window": true,
      "is_aisle": false,
      "has_extra_legroom": true,
      "price_multiplier": 1.25,
      "status": "booked",
      "price": 25000.0
    }
  ],
  "seats_by_row": {
    "1": [
      /* seat objects */
    ],
    "2": [
      /* seat objects */
    ]
  }
}
```

## Fare Calculation Logic

### Formula

```python
base_fare = trip.base_fare  # e.g., 20,000 UGX
seat_multiplier = seat.price_multiplier  # e.g., 1.25 for premium

# Option 1: If trip has pricing configuration
if trip.pricing:
    total = trip.pricing.calculate_final_fare(seat_multiplier)
    # Accounts for peak season, demand, early bird discounts
else:
    # Option 2: Simple calculation
    total = base_fare * seat_multiplier

seat_fee = total - base_fare
service_fee = 0  # Currently 0 for direct bookings

final_total = base_fare + seat_fee + service_fee
```

### Examples

**Regular Seat (multiplier = 1.0)**

- Base Fare: 20,000 UGX
- Seat Fee: 0 UGX
- **Total: 20,000 UGX**

**Premium Seat (multiplier = 1.25)**

- Base Fare: 20,000 UGX
- Seat Fee: 5,000 UGX
- **Total: 25,000 UGX**

**VIP Seat (multiplier = 1.5)**

- Base Fare: 20,000 UGX
- Seat Fee: 10,000 UGX
- **Total: 30,000 UGX**

## Testing the System

### 1. Using Django Admin

```bash
# Create test data
python manage.py shell

from companies.models import Company, Bus, BusSeat
from trips.models import Route, Trip
from django.utils import timezone

# Create route
route = Route.objects.create(
    company=your_company,
    name="Kampala to Gulu",
    origin_city="Kampala",
    destination_city="Gulu",
    base_fare=20000,
    distance_km=350
)

# Create trip (tomorrow)
trip = Trip.objects.create(
    company=your_company,
    route=route,
    bus=your_bus,
    departure_date=timezone.now().date() + timedelta(days=1),
    departure_time="08:00",
    arrival_time="14:00",
    base_fare=20000
)
```

### 2. Test Booking via Web

1. Login as company staff
2. Go to `/company/bookings/create/`
3. Select the route and date
4. Choose trip
5. Click any green seat
6. **Verify fare shows correctly**
7. Complete booking

### 3. Test Booking via API

```bash
# Get auth token first
curl -X POST http://localhost:8000/api/mobile/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com", "password":"yourpassword"}'

# Use token to create booking
curl -X POST http://localhost:8000/api/mobile/bookings/create/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "trip": 1,
    "seat_number": "1A",
    "passenger_name": "Test User",
    "passenger_phone": "0700000000"
  }'
```

## Common Issues & Solutions

### Issue: "Seat is already booked"

**Cause**: Someone else booked it, or there's an active reservation
**Solution**: Choose a different seat (green status only)

### Issue: "Trip is not available for booking"

**Cause**: Trip departed, canceled, or no seats left
**Solution**: Select a different trip

### Issue: Fare not calculating

**Cause**: Trip might not have pricing configured
**Solution**: System falls back to base_fare \* seat_multiplier

### Issue: Can't see any trips

**Cause**: No scheduled trips for that route/date
**Solution**: Check route has active trips in future dates

## Mobile App Integration Checklist

- [ ] Implement JWT authentication
- [ ] Store token securely
- [ ] Call GET /api/mobile/trips/search/ for trip list
- [ ] Call GET /api/mobile/trips/{id}/ for seat map
- [ ] Display seats in grid (use seat status colors)
- [ ] Show fare breakdown on seat selection
- [ ] Call POST /api/mobile/bookings/create/ to book
- [ ] Display QR code from booking response
- [ ] Handle error states (seat taken, trip full, etc.)

## Next Payment Integration

Once booking is created with status PENDING:

```python
# Step 1: User selects payment method
# Step 2: Create payment record
payment = Payment.objects.create(
    company=booking.company,
    booking=booking,
    user=booking.passenger,
    amount=booking.total_amount,
    payment_method='MOBILE_MONEY',
    status='PENDING'
)

# Step 3: Initiate payment with gateway (MTN, Airtel, etc.)
# Step 4: On success callback, mark payment complete
payment.status = 'COMPLETED'
payment.save()

# Step 5: Confirm the booking
booking.confirm_booking()  # Updates trip.booked_seats, status=CONFIRMED
```

## Support

For issues or questions:

1. Check BOOKING_IMPLEMENTATION.md for detailed technical docs
2. Review existing API endpoints in `bookings/direct_booking_views.py`
3. Test mobile endpoints in `api/tests/test_mobile_booking.py`
