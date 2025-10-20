from django.core.management.base import BaseCommand
from companies.models import Bus, BusSeat
from django.db import transaction


class Command(BaseCommand):
    help = "Create seatmaps for buses that do not have seats yet (2-2 layout)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--bus", type=str, help="License plate of a specific bus to backfill"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        bus_plate = options.get("bus")
        if bus_plate:
            buses = Bus.objects.filter(license_plate=bus_plate)
            if not buses.exists():
                self.stdout.write(self.style.ERROR(f"Bus {bus_plate} not found"))
                return
        else:
            buses = Bus.objects.all()

        updated = 0
        for bus in buses:
            if bus.total_seats and not bus.seats.exists():
                self._create_seats(bus)
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created seats for {bus.license_plate}")
                )
            else:
                self.stdout.write(
                    f"Skipping {bus.license_plate}: seats already exist or total_seats not set"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Backfill complete. {updated} buses updated.")
        )

    def _create_seats(self, bus: Bus):
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
