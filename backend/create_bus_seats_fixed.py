#!/usr/bin/env python
"""
Script to create seats for a bus - FIXED VERSION
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookutu.settings")
django.setup()

from companies.models import Bus, BusSeat
from trips.models import Trip

# Get the bus from the trip
trip = Trip.objects.first()
bus = trip.bus

print(f"Creating seats for bus: {bus.license_plate}")
print(f"Total seats to create: {bus.total_seats}")

# Delete any existing seats
deleted_count = bus.seats.all().delete()[0]
print(f"Deleted {deleted_count} existing seats\n")

# Create seats based on bus layout
# Standard bus layout: 2-2 seating (2 seats on each side of aisle)
seats_per_row = 4
rows = (bus.total_seats + seats_per_row - 1) // seats_per_row

seat_number = 1
seats_created = 0

# Position mapping
position_map = {1: "LEFT_WINDOW", 2: "LEFT_AISLE", 3: "RIGHT_AISLE", 4: "RIGHT_WINDOW"}

for row in range(1, rows + 1):
    row_seats = []

    # Create all 4 seats for this row (if we have enough seats left)
    for pos in range(1, 5):
        if seats_created >= bus.total_seats:
            break

        seat = BusSeat.objects.create(
            bus=bus,
            seat_number=f"{seat_number:02d}",
            row_number=row,
            seat_position=position_map[pos],
            seat_type="STANDARD",
            is_window=(pos in [1, 4]),
            is_aisle=(pos in [2, 3]),
            has_extra_legroom=(row == 1),
            price_multiplier=1.2 if row == 1 else 1.0,
        )
        row_seats.append(f"{seat.seat_number}({position_map[pos]})")
        seat_number += 1
        seats_created += 1

    print(f"Row {row}: {', '.join(row_seats)}")

print(f"\n✅ Total seats created: {seats_created}")
print(f"✅ Seats in database: {bus.seats.count()}")
