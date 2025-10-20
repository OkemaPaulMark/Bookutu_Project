# Bookutu Booking System - Visual Flow

## Web Booking Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPANY STAFF LOGIN                              │
│                 (Django Session Authentication)                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Route & Trip Selection                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Route: [Kampala → Gulu ▼]                                    │  │
│  │  Date:  [2025-10-20 📅]                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Available Trips:                                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ 08:00 - 14:00  │  UAA123A  │  LUXURY     │  UGX 20,000    │    │
│  │ ✓ AC  ✓ WiFi  │  25 seats left                            │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Seat Selection & Fare Display                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Bus Layout: UAA123A                              │  │
│  │                                                               │  │
│  │              🚗  [Driver]                                     │  │
│  │                                                               │  │
│  │   Row 1:  [1A]  [1B]     AISLE     [1C]  [1D]               │  │
│  │            🟢    🟢                  🟢    🔴                  │  │
│  │                                                               │  │
│  │   Row 2:  [2A]  [2B]     AISLE     [2C]  [2D]               │  │
│  │            🟢    🔴                  🟢    🟢                  │  │
│  │                                                               │  │
│  │   Row 3:  [3A]  [3B]     AISLE     [3C]  [3D]               │  │
│  │            🔵    🟡                  🟢    🟢                  │  │
│  │         SELECTED RESERVED                                     │  │
│  │                                                               │  │
│  │  Legend: 🟢 Available  🔵 Selected  🔴 Booked  🟡 Reserved   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────┐                                 │
│  │   SELECTION SUMMARY            │                                 │
│  │                                │                                 │
│  │   Seat: 3A (Premium)           │                                 │
│  │                                │                                 │
│  │   Base Fare:    UGX 20,000    │                                 │
│  │   Seat Fee:     UGX  5,000    │                                 │
│  │   ─────────────────────────    │                                 │
│  │   Total:        UGX 25,000    │                                 │
│  │                                │                                 │
│  │  [Proceed to Passenger →]     │                                 │
│  └────────────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Passenger Details                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Name:    [John Doe...........................]  *            │  │
│  │  Phone:   [0700000000......................]  *            │  │
│  │  Email:   [john@example.com................]               │  │
│  │  ID:      [CM123456XYZ.....................]               │  │
│  │                                                               │  │
│  │  [← Back]              [Proceed to Confirmation →]           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Confirmation                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  Trip Details    │  │ Passenger Info   │  │ Payment Summary │  │
│  │                  │  │                  │  │                 │  │
│  │  Kampala→Gulu   │  │  John Doe        │  │  Base: 20,000  │  │
│  │  2025-10-20     │  │  0700000000      │  │  Seat:  5,000  │  │
│  │  08:00          │  │  john@.com       │  │  ────────────  │  │
│  │  Seat: 3A       │  │                  │  │  Total: 25,000 │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
│                                                                      │
│  [← Back]           [✓ Confirm & Create Booking]                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ✓ SUCCESS!                                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Booking Created Successfully!                     │  │
│  │                                                               │  │
│  │          Booking Reference: BK20251019ABC123                  │  │
│  │                                                               │  │
│  │          [Create Another Booking]  [View All Bookings]       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Mobile API Booking Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MOBILE APP USER                                  │
│                  (JWT Token Authentication)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Search Trips                                                        │
│  POST /api/mobile/trips/search/                                     │
│  {                                                                   │
│    "origin": "Kampala",                                             │
│    "destination": "Gulu",                                           │
│    "departure_date": "2025-10-20",                                  │
│    "passengers": 1                                                  │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Get Trip Details & Seat Map                                        │
│  GET /api/mobile/trips/5/                                           │
│                                                                      │
│  Response includes:                                                  │
│  - Trip info (times, bus, company)                                  │
│  - Seat array with:                                                 │
│    • id, seat_number, seat_type                                     │
│    • price (calculated with multiplier)                             │
│    • is_available (true/false)                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Display Seat Map in App                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Tap seat to select:                                          │  │
│  │                                                               │  │
│  │  [ 1A ]  [ 1B ]      [ 1C ]  [ 1D ]                          │  │
│  │  20,000  20,000      20,000  TAKEN                           │  │
│  │                                                               │  │
│  │  [ 2A ]  [ 2B ]      [ 2C ]  [ 2D ]                          │  │
│  │  20,000  TAKEN       20,000  20,000                          │  │
│  │                                                               │  │
│  │  [ 3A ]  [ 3B ]      [ 3C ]  [ 3D ]                          │  │
│  │ ►25,000◄ HOLD        20,000  20,000                          │  │
│  │ SELECTED                                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Selected: Seat 3A - UGX 25,000                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Create Booking                                                      │
│  POST /api/mobile/bookings/create/                                  │
│  Headers: Authorization: Bearer <JWT_TOKEN>                         │
│  {                                                                   │
│    "trip": 5,                                                       │
│    "seat": 12,                    // or "seat_number": "3A"         │
│    "passenger_name": "John Doe",                                    │
│    "passenger_phone": "0700000000"                                  │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Backend Processing (Atomic Transaction)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Validate trip is bookable                                 │  │
│  │  2. Check seat belongs to trip bus                            │  │
│  │  3. Verify seat not already booked                            │  │
│  │  4. Create SeatReservation (race condition guard)             │  │
│  │  5. Calculate pricing:                                         │  │
│  │     - base_fare from trip                                      │  │
│  │     - seat_fee from multiplier                                 │  │
│  │     - service_fee (currently 0)                                │  │
│  │  6. Create Booking (status=PENDING, source=MOBILE_APP)        │  │
│  │  7. Return booking object                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Success Response (201)                                              │
│  {                                                                   │
│    "message": "Booking created successfully",                       │
│    "booking": {                                                     │
│      "id": 123,                                                     │
│      "booking_reference": "BK20251019ABC123",                       │
│      "status": "PENDING",                                           │
│      "total_amount": "25000.00",                                    │
│      "seat_info": {                                                 │
│        "seat_number": "3A",                                         │
│        "price": 25000.0                                             │
│      },                                                             │
│      "qr_code": "BOOKUTU:BK20251019ABC123:123"                      │
│    }                                                                 │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Display in App                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ✓ Booking Confirmed!                                         │  │
│  │                                                               │  │
│  │  Reference: BK20251019ABC123                                  │  │
│  │                                                               │  │
│  │  █████████                                                    │  │
│  │  ██ ▄▄▄ ██    QR Code                                         │  │
│  │  ██ ███ ██                                                    │  │
│  │  █████████                                                    │  │
│  │                                                               │  │
│  │  Kampala → Gulu                                               │  │
│  │  Oct 20, 2025 at 08:00                                        │  │
│  │  Seat: 3A  |  Total: UGX 25,000                              │  │
│  │                                                               │  │
│  │  Status: PENDING PAYMENT                                      │  │
│  │                                                               │  │
│  │  [Proceed to Payment]                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Schema (Key Tables)

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Company    │◄──────┤     Trip     │───────►│     Bus      │
└──────────────┘       └──────────────┘       └──────────────┘
                              │                       │
                              │                       │
                              ▼                       ▼
                       ┌──────────────┐       ┌──────────────┐
                       │    Booking   │───────►│   BusSeat    │
                       └──────────────┘       └──────────────┘
                              │
                              │
                              ▼
                       ┌──────────────┐
                       │   Payment    │
                       └──────────────┘

Trip Fields:
- company, route, bus
- departure_date, departure_time
- base_fare (UGX 20,000)
- status (SCHEDULED, etc.)
- available_seats, booked_seats

BusSeat Fields:
- bus, seat_number (e.g., "3A")
- seat_type (REGULAR, PREMIUM, VIP)
- price_multiplier (1.0, 1.25, 1.5)
- is_window, is_aisle

Booking Fields:
- company, trip, passenger, seat
- status (PENDING, CONFIRMED)
- source (MOBILE_APP, WEB, DIRECT)
- base_fare, seat_fee, service_fee
- total_amount = base_fare + seat_fee + service_fee
- booking_reference (unique)

SeatReservation Fields:
- trip, seat, user
- expires_at (15 minutes)
- is_active
- unique_together: (trip, seat) ← prevents double-booking
```

## Fare Calculation Examples

```
Trip Base Fare: UGX 20,000

┌─────────────┬────────────────┬──────────┬──────────┬────────────┐
│ Seat Type   │ Multiplier     │ Base     │ Seat Fee │ Total      │
├─────────────┼────────────────┼──────────┼──────────┼────────────┤
│ REGULAR     │ 1.0            │ 20,000   │ 0        │ 20,000     │
│ PREMIUM     │ 1.25           │ 20,000   │ 5,000    │ 25,000     │
│ VIP         │ 1.5            │ 20,000   │ 10,000   │ 30,000     │
│ SLEEPER     │ 2.0            │ 20,000   │ 20,000   │ 40,000     │
└─────────────┴────────────────┴──────────┴──────────┴────────────┘

Formula:
  total = base_fare × multiplier
  seat_fee = total - base_fare
  final_amount = base_fare + seat_fee + service_fee
```

## Error Handling Flow

```
POST /api/mobile/bookings/create/
         │
         ├─► Validation Errors (400)
         │   ├─ "Trip is not available for booking"
         │   ├─ "Seat is already booked"
         │   ├─ "Seat does not belong to trip bus"
         │   └─ "Seat is currently reserved"
         │
         ├─► Authentication Errors (401)
         │   └─ "Invalid or expired token"
         │
         ├─► Not Found (404)
         │   ├─ "Trip not found"
         │   └─ "Seat not found"
         │
         └─► Success (201)
             └─ Booking object with reference
```

## Concurrent Booking Prevention

```
User A                    User B
  │                         │
  ├─ Click Seat 3A         │
  │  (reserve)              │
  │                         ├─ Click Seat 3A
  ├─ Create reservation    │  (reserve attempt)
  │  ✓ SUCCESS              │
  │                         ├─ Create reservation
  │                         │  ✗ FAIL (unique constraint)
  │                         │  Error: "Seat currently reserved"
  ├─ Complete booking      │
  │  ✓ Booking created     │
  │  Seat marked BOOKED    │
  │                         │
  └─ Reservation cleared   └─ Must choose different seat
```

This is powered by:

1. Database unique_together constraint on (trip, seat) in SeatReservation
2. Transaction.atomic() wrapping the booking creation
3. Active reservation check before allowing booking
