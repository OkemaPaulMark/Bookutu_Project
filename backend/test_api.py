#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookutu.settings")
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from bookings.direct_booking_views import (
    DirectBookingRoutesView,
    DirectBookingTripsView,
    DirectBookingSeatsView,
)

User = get_user_model()

# Get staff user
user = User.objects.filter(user_type="COMPANY_STAFF").first()
print(f"User: {user.email}")
print(f"Company: {user.company}")
print(f"Company active: {user.company.is_active()}")
print()

# Test routes endpoint
factory = RequestFactory()
request = factory.get("/api/v1/bookings/direct/routes/")
request.user = user

view = DirectBookingRoutesView.as_view()
response = view(request)

print(f"Routes Response Status: {response.status_code}")
print(f"Routes Data: {response.data}")
print()

# Test trips endpoint
request = factory.get(
    "/api/v1/bookings/direct/trips/?route_id=1&departure_date=2025-10-20"
)
request.user = user

view = DirectBookingTripsView.as_view()
response = view(request)

print(f"Trips Response Status: {response.status_code}")
print(f"Trips Data: {response.data}")
print()

# Test seats endpoint
request = factory.get("/api/v1/bookings/direct/trips/1/seats/")
request.user = user

view = DirectBookingSeatsView.as_view()
response = view(request, trip_id=1)

print(f"Seats Response Status: {response.status_code}")
print(f"Total seats: {response.data.get('total_seats')}")
print(f"Available seats: {response.data.get('available_seats')}")
print(f"Seats count: {len(response.data.get('seats', []))}")
if response.data.get("seats"):
    print(f"First seat: {response.data['seats'][0]}")
