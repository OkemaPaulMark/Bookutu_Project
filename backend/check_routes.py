#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookutu.settings")
django.setup()

from trips.models import Route, Trip
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Get staff user
staff = User.objects.filter(user_type="COMPANY_STAFF").first()
print(f"Staff user: {staff}")
print(f"Company: {staff.company if staff else None}")
print()

# Check routes
all_routes = Route.objects.filter(company=staff.company if staff else None)
print(f"Total routes for company: {all_routes.count()}")

# Check routes with upcoming trips
routes_with_trips = Route.objects.filter(
    company=staff.company if staff else None,
    is_active=True,
    trips__departure_date__gte=timezone.now().date(),
    trips__status="SCHEDULED",
).distinct()

print(f"Routes with upcoming scheduled trips: {routes_with_trips.count()}")
for route in routes_with_trips:
    print(f"  - {route.origin_city} → {route.destination_city}")
    upcoming = route.trips.filter(
        departure_date__gte=timezone.now().date(), status="SCHEDULED"
    )
    print(f"    Upcoming trips: {upcoming.count()}")
    for trip in upcoming[:3]:
        print(f"      * {trip.departure_date} {trip.departure_time}")
print()

# Check all trips
all_trips = Trip.objects.filter(company=staff.company if staff else None)
print(f"Total trips for company: {all_trips.count()}")
scheduled_trips = all_trips.filter(status="SCHEDULED")
print(f"Scheduled trips: {scheduled_trips.count()}")
future_trips = scheduled_trips.filter(departure_date__gte=timezone.now().date())
print(f"Future scheduled trips: {future_trips.count()}")
