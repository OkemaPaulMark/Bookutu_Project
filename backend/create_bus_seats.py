#!/usr/bin/env python
"""
Script to create seats for a bus
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
bus.seats.all().delete()

# Create seats based on bus layout
# Standard bus layout: 2-2 seating (2 seats on each side of aisle)
# For 34 seats: 8.5 rows (let's make it 9 rows with 2 seats in last row)

seats_per_row = 4  # 2 on left, 2 on right
rows = (bus.total_seats + seats_per_row - 1) // seats_per_row

seat_number = 1
seats_created = 0

for row in range(1, rows + 1):
    # Left side - 2 seats
    for pos in range(1, 3):
        if seats_created >= bus.total_seats:
            break

        seat = BusSeat.objects.create(
            bus=bus,
            seat_number=f"{seat_number:02d}",
            row_number=row,
            seat_position=pos,  # 1 or 2 on left side
            seat_type="STANDARD",
            is_window=(pos == 1),  # Position 1 is window
            is_aisle=(pos == 2),  # Position 2 is aisle
            has_extra_legroom=(row == 1),  # First row has extra legroom
            price_multiplier=1.2 if row == 1 else 1.0,  # Premium for first row
        )
        print(f"Created seat {seat.seat_number} - Row {row}, Left {pos}")
        seat_number += 1
        seats_created += 1

    if seats_created >= bus.total_seats:
        break

    # Right side - 2 seats
    for pos in range(3, 5):
        if seats_created >= bus.total_seats:
            break

        seat = BusSeat.objects.create(
            bus=bus,
            seat_number=f"{seat_number:02d}",
            row_number=row,
            seat_position=pos,  # 3 or 4 on right side
            seat_type="STANDARD",
            is_window=(pos == 4),  # Position 4 is window
            is_aisle=(pos == 3),  # Position 3 is aisle
            has_extra_legroom=(row == 1),  # First row has extra legroom
            price_multiplier=1.2 if row == 1 else 1.0,  # Premium for first row
        )
        print(f"Created seat {seat.seat_number} - Row {row}, Right {pos-2}")
        seat_number += 1
        seats_created += 1

print(f"\nTotal seats created: {seats_created}")
print(f"Seats in database: {bus.seats.count()}")
