# Mobile API Fixes - Passenger Authentication Support

## Summary

Fixed the mobile API to support **passenger authentication** for bookings while maintaining compatibility with the existing User model that's designed for company staff.

## Changes Made

### 1. User Model (`accounts/models.py`)

- **Made `user_type` field blankable** to allow passenger/guest users who are not company staff
- **Updated `save()` method** to handle non-staff users (passengers/guests) who don't need a company assigned
- Staff users (COMPANY_STAFF, SUPER_ADMIN) still require proper validation

```python
# Before: user_type required COMPANY_STAFF by default
user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='COMPANY_STAFF')

# After: user_type can be empty for passengers
user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='COMPANY_STAFF', blank=True)
```

### 2. Mobile Registration (`api/mobile_views.py`)

- **Fixed `mobile_register` function** to create passenger users with empty `user_type`
- **Fixed PassengerProfile creation** to use correct field names:
  - `emergency_contact` → `emergency_contact_name`
  - `emergency_phone` → `emergency_contact_phone`
- Added `gender` field support

### 3. Mobile Booking Creation (`api/mobile_views.py`)

- **Kept permission as `IsAuthenticated`** on `MobileBookingCreateView`
- Passengers must register/login before booking

### 4. Booking Serializer (`api/mobile_serializers.py`)

- **Simplified `MobileBookingCreateSerializer.create()`:**
  - Uses authenticated user from request
  - Creates seat reservation to avoid race conditions
  - Falls back to user profile data for passenger info if not provided

### 5. Test Fixes (`api/tests/test_mobile_booking.py`)

- **Updated test setup** to create passenger users with `user_type=''`
- **Added authentication** using `force_authenticate()` for test user
- **Fixed seat generation** to use auto-generated seats from `Bus.save()` instead of manually creating duplicates
- **Fixed assertion** to compare actual seat number instead of hardcoded value

## How Passenger Booking Works

1. **Registration**: Passenger registers via `/api/mobile/auth/register/`
2. **Login**: Passenger logs in via `/api/mobile/auth/login/` to get JWT token
3. **Booking**: Passenger calls `/api/mobile/bookings/create/` with JWT token
4. **Authorization**: System uses authenticated user from JWT token
5. **Booking Created**: Booking is created and linked to the authenticated user

## Test Results

All 3 mobile booking API tests passing:

- ✅ `test_create_booking_success` - Authenticated booking with passenger user
- ✅ `test_create_booking_seat_already_booked` - Validates seat availability
- ✅ `test_create_booking_invalid_seat_for_bus` - Validates seat belongs to bus

## API Endpoints

### 1. User Registration (No Auth Required)

```
POST /api/mobile/auth/register/
{
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "0700123456",
    "gender": "M",  // optional
    "date_of_birth": "1990-01-01",  // optional
    "emergency_contact": "Jane Doe",  // optional
    "emergency_phone": "0700654321"  // optional
}
```

### 2. User Login (Get JWT Token)

```
POST /api/mobile/auth/login/
{
    "email": "user@example.com",
    "password": "securepass123"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

### 3. Create Booking (Auth Required)

```
POST /api/mobile/bookings/create/
Headers: Authorization: Bearer <access_token>

{
    "trip": 1,
    "seat": 5,
    "passenger_name": "John Doe",  // optional, defaults to user name
    "passenger_phone": "0700123456",  // optional, defaults to user phone
    "passenger_email": "john@example.com"  // optional, defaults to user email
}
```

## Compatibility Notes

- **Web App (Company Staff)**: Not affected - still requires COMPANY_STAFF user_type and company assignment
- **Mobile App (Passengers)**: Must register/login to book - passengers have `user_type=''` (empty)
- **Existing Users**: No migration needed - existing staff users work as before
- **Database**: No schema changes required - only code logic updates

## Testing with Demo Data

To test the mobile API:

1. **Create a test passenger user** (via Django admin or shell):

```python
from django.contrib.auth import get_user_model
User = get_user_model()

passenger = User.objects.create_user(
    email="testpassenger@example.com",
    password="testpass123",
    first_name="Test",
    last_name="Passenger",
    phone_number="0700123456",
    user_type=''  # Empty for passengers
)
```

2. **Login via API** to get JWT token
3. **Use token** to create bookings via `/api/mobile/bookings/create/`

## Next Steps

Consider adding:

- [ ] Password reset for passengers
- [ ] Email verification for new registrations
- [ ] Booking history view for passengers
- [ ] Payment integration for bookings
