from companies.models import Bus, BusSeat
from django.db import transaction

# Run with: python manage.py shell < scripts/backfill_bus_seats.py


def create_seats_for_bus(bus):
    if bus.seats.exists() or bus.total_seats < 1:
        return
    seats_per_row = 4
    num_rows = bus.total_seats // seats_per_row
    seat_positions = ["LEFT_WINDOW", "LEFT_AISLE", "RIGHT_AISLE", "RIGHT_WINDOW"]
    seat_letters = ["A", "B", "C", "D"]
    for row in range(1, num_rows + 1):
        for i in range(seats_per_row):
            seat_number = f"{row}{seat_letters[i]}"
            BusSeat.objects.create(
                bus=bus,
                seat_number=seat_number,
                row_number=row,
                seat_position=seat_positions[i],
                seat_type="REGULAR",
                is_window=(i == 0 or i == 3),
                is_aisle=(i == 1 or i == 2),
                has_extra_legroom=False,
                price_multiplier=1.00,
            )


@transaction.atomic
def main():
    buses = Bus.objects.all()
    count = 0
    for bus in buses:
        if not bus.seats.exists():
            create_seats_for_bus(bus)
            print(f"Created seats for bus {bus.license_plate}")
            count += 1
    print(f"Backfill complete. {count} buses updated.")


main()
