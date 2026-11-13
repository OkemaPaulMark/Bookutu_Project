"""
Seed demo data so the mobile app and dashboards have something real to show.

    python manage.py seed_demo            # (re)create demo trips for the next 7 days
    python manage.py seed_demo --days 14

Safe to re-run: companies, routes, buses and users are reused; demo trips
(and their bookings/payments) are deleted and regenerated so dates stay current.
"""
import random
import uuid
from datetime import datetime, timedelta, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User, PassengerProfile
from bookings.models import Booking
from companies.models import Company, Bus, CompanySettings
from notifications.models import Announcement
from payments.models import Payment
from trips.models import Route, Trip

DEMO_TAG = "DEMO_SEED"
DEMO_EMAIL = "demo@bookutu.com"
DEMO_PASSWORD = "Demo@1234"

# company slug -> (bus image, routes)
# route: (origin, origin terminal, destination, destination terminal, km, hours, fare, stops, departure)
PLAN = {
    "global": ("buses/Global_bus.jpg", [
        ("Kampala", "Namayiba Bus Terminal", "Gulu", "Gulu Main Park", 340, 5.5, 40000, ["Luweero", "Kigumba"], time(7, 0)),
        ("Gulu", "Gulu Main Park", "Kampala", "Namayiba Bus Terminal", 340, 5.5, 40000, [], time(8, 0)),
        ("Kampala", "Namayiba Bus Terminal", "Arua", "Arua Bus Park", 480, 8.0, 60000, ["Gulu"], time(6, 0)),
    ]),
    "yy": ("buses/yy.jpg", [
        ("Kampala", "Qualicel Bus Terminal", "Mbarara", "Mbarara Main Park", 270, 4.5, 35000, ["Masaka"], time(9, 0)),
        ("Mbarara", "Mbarara Main Park", "Kampala", "Qualicel Bus Terminal", 270, 4.5, 35000, ["Masaka"], time(7, 30)),
        ("Kampala", "Qualicel Bus Terminal", "Kabale", "Kabale Bus Park", 410, 7.0, 50000, ["Masaka", "Mbarara"], time(6, 30)),
    ]),
    "tausi": ("buses/tausi.jpg", [
        ("Kampala", "Old Taxi Park", "Jinja", "Jinja Main Park", 80, 2.0, 15000, ["Mukono"], time(10, 0)),
        ("Kampala", "Old Taxi Park", "Mbale", "Mbale Bus Park", 245, 4.5, 30000, ["Jinja", "Iganga"], time(8, 30)),
        ("Mbale", "Mbale Bus Park", "Kampala", "Old Taxi Park", 245, 4.5, 30000, ["Iganga", "Jinja"], time(13, 0)),
    ]),
    "trinity": (["buses/coach_fleet.jpg", "buses/coach_road.jpg", "buses/coach_night.jpg"], [
        ("Kampala", "Kisenyi Bus Park", "Fort Portal", "Fort Portal Bus Park", 300, 5.0, 35000, ["Mityana"], time(8, 0)),
        ("Kampala", "Kisenyi Bus Park", "Masaka", "Masaka Bus Park", 135, 2.5, 20000, [], time(11, 0)),
        ("Kampala", "Kisenyi Bus Park", "Hoima", "Hoima Bus Park", 230, 4.0, 30000, [], time(14, 0)),
    ]),
}

FIRST = ["Aisha", "Brian", "Catherine", "David", "Esther", "Fred", "Grace", "Henry", "Irene",
         "Joseph", "Kevin", "Lydia", "Moses", "Naomi", "Owen", "Patience", "Ronald", "Sarah"]
LAST = ["Nakato", "Okello", "Achieng", "Mugisha", "Namubiru", "Ssali", "Atim", "Kato",
        "Nansubuga", "Opio", "Tumusiime", "Akello"]

ANNOUNCEMENTS = [
    ("Welcome to Bookutu", "Book bus tickets across Uganda, pick your seat and pay with MTN or Airtel Money.", "medium"),
    ("Live bus tracking", "Open the Location tab to see buses on the road right now and their estimated progress.", "low"),
    ("Holiday travel", "Seats on Kampala–Gulu and Kampala–Mbarara fill fast in December. Book early!", "high"),
]


def combine(d, t):
    return timezone.make_aware(datetime.combine(d, t))


class Command(BaseCommand):
    help = "Seed demo companies' routes, buses, trips, passengers and bookings"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7)

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(42)
        now = timezone.localtime()
        today = now.date()

        # Remove previous demo trips (cascades to bookings, payments, pricing)
        deleted, _ = Trip.objects.filter(notes=DEMO_TAG).delete()
        self.stdout.write(f"Removed {deleted} old demo rows")

        demo_user = self._passenger(DEMO_EMAIL, "Demo", "Passenger", "+256700123456", DEMO_PASSWORD)
        others = [
            self._passenger(f"passenger{i:02d}@demo.bookutu.com", FIRST[i % len(FIRST)],
                            LAST[i % len(LAST)], f"+2567{70000000 + i * 1371:08d}", DEMO_PASSWORD)
            for i in range(18)
        ]

        all_trips = []
        plate_no = 100
        for slug, (image, routes) in PLAN.items():
            company = Company.objects.filter(slug=slug).first()
            if not company:
                company = Company.objects.create(
                    name=slug.title(), slug=slug, email=f"info@{slug}.co.ug",
                    phone_number="+256700000000", address="Kampala", city="Kampala",
                    state="Central", registration_number=f"DEMO-{slug.upper()}",
                    license_number=f"LIC-{slug.upper()}", status="ACTIVE")
            CompanySettings.objects.get_or_create(company=company)

            for idx, (o, ot, d, dt, km, hrs, fare, stops, dep) in enumerate(routes):
                route, _ = Route.objects.update_or_create(
                    company=company, origin_city=o, destination_city=d,
                    defaults=dict(name=f"{o} to {d}", origin_terminal=ot, destination_terminal=dt,
                                  distance_km=km, estimated_duration_hours=Decimal(str(hrs)),
                                  base_fare=Decimal(fare), is_active=True,
                                  intermediate_stops=[{"city": s, "duration_minutes": 15} for s in stops]))
                plate_no += 1
                photo = image[idx % len(image)] if isinstance(image, list) else image
                bus = self._bus(company, f"UB{chr(65 + idx)} {plate_no}{slug[0].upper()}",
                                photo, 44 if idx % 2 else 48, ["STANDARD", "LUXURY", "VIP"][idx % 3])
                live_bus = self._bus(company, f"UB{chr(65 + idx)} {plate_no + 500}{slug[0].upper()}",
                                     photo, 44, "STANDARD")

                duration = timedelta(hours=hrs)
                for day in range(0, opts["days"]):
                    date = today + timedelta(days=day)
                    # vary departure a little by day
                    start = (datetime.combine(date, dep) + timedelta(minutes=30 * (day % 3))).time()
                    if day == 0 and combine(date, start) <= now:
                        continue  # morning trip already left; the live bus covers today
                    t = self._trip(company, route, bus, date, start, duration, "SCHEDULED")
                    if t:
                        all_trips.append(t)

                # A bus on the road right now, for the live map
                frac = 0.15 + 0.7 * rng.random()
                live_dep = now - duration * frac
                if live_dep.date() == today and (live_dep + duration).date() == today:
                    self._trip(company, route, live_bus, today, live_dep.time().replace(second=0, microsecond=0),
                               duration, "IN_TRANSIT")

                # A completed trip last week, for booking history
                past = self._trip(company, route, live_bus, today - timedelta(days=7 + idx), dep, duration, "COMPLETED")
                if past and slug == "yy" and idx == 0:
                    self._book(past, past.bus.seats.order_by("row_number", "seat_number")[2], demo_user, "COMPLETED", "MTN")

        # Fill upcoming trips with other passengers so seat maps look real
        booked = 0
        for trip in all_trips:
            seats = list(trip.bus.seats.all())
            for seat in rng.sample(seats, int(len(seats) * rng.uniform(0.2, 0.6))):
                self._book(trip, seat, rng.choice(others), "CONFIRMED", rng.choice(["MTN", "AIRTEL", "CASH"]))
                booked += 1

        # Demo passenger's own bookings
        upcoming = sorted([t for t in all_trips if t.departure_date > today],
                          key=lambda t: (t.departure_date, t.departure_time))
        if upcoming:
            def free_seat(trip):
                taken = set(Booking.objects.filter(trip=trip, status__in=["PENDING", "CONFIRMED"])
                            .values_list("seat_id", flat=True))
                return next(s for s in trip.bus.seats.order_by("row_number", "seat_number") if s.id not in taken)
            self._book(upcoming[0], free_seat(upcoming[0]), demo_user, "CONFIRMED", "MTN")
            self._book(upcoming[len(upcoming) // 2], free_seat(upcoming[len(upcoming) // 2]), demo_user, "PENDING", None)
            c = self._book(upcoming[-1], free_seat(upcoming[-1]), demo_user, "PENDING", None)
            c.cancel_booking("Changed travel plans")

        # Announcements
        author = User.objects.filter(is_superuser=True).first() or demo_user
        for title, msg, prio in ANNOUNCEMENTS:
            Announcement.objects.update_or_create(
                title=title, defaults=dict(message=msg, priority=prio, target_audience="passengers",
                                           created_by=author, is_active=True))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(all_trips)} upcoming trips, {booked} passenger bookings.\n"
            f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}"))

    # ------------------------------------------------------------------ helpers
    def _passenger(self, email, first, last, phone, password):
        user, created = User.objects.get_or_create(
            email=email, defaults=dict(first_name=first, last_name=last, phone_number=phone,
                                       user_type="PASSENGER", is_verified=True))
        if created:
            user.set_password(password)
            user.save()
        PassengerProfile.objects.get_or_create(user=user)
        return user

    def _bus(self, company, plate, image, seats, bus_type):
        bus, created = Bus.objects.get_or_create(
            license_plate=plate,
            defaults=dict(company=company, model="Higer KLQ6129", make="Higer", year=2022,
                          total_seats=seats, bus_type=bus_type, has_ac=True,
                          has_wifi=bus_type != "STANDARD", has_charging_ports=True,
                          has_entertainment=bus_type == "VIP", has_restroom=bus_type == "VIP",
                          status="ACTIVE", image=image))
        if not created and bus.image.name != image:
            Bus.objects.filter(pk=bus.pk).update(image=image)
        return bus

    def _trip(self, company, route, bus, date, start, duration, status):
        arrival = (datetime.combine(date, start) + duration)
        if arrival.date() != date:
            return None  # model requires same-day arrival
        trip = Trip(company=company, route=route, bus=bus, departure_date=date,
                    departure_time=start, arrival_time=arrival.time().replace(second=0, microsecond=0),
                    base_fare=route.base_fare, status=status, available_seats=bus.total_seats,
                    notes=DEMO_TAG, driver_name=None)
        try:
            trip.save()
        except Exception as e:  # schedule conflict etc.
            self.stderr.write(f"skip trip {route} {date} {start}: {e}")
            return None
        return trip

    def _book(self, trip, seat, user, status, method):
        fare = trip.base_fare * seat.price_multiplier
        b = Booking.objects.create(
            company=trip.company, trip=trip, passenger=user, seat=seat, status=status,
            source=random.choice(["MOBILE_APP", "WEB", "DIRECT"]),
            passenger_name=f"{user.first_name} {user.last_name}", passenger_phone=user.phone_number,
            passenger_email=user.email, base_fare=trip.base_fare, seat_fee=fare - trip.base_fare,
            total_amount=fare,
            confirmed_at=timezone.now() if status in ("CONFIRMED", "COMPLETED") else None)
        if status in ("CONFIRMED", "COMPLETED"):
            Trip.objects.filter(pk=trip.pk).update(booked_seats=trip.booked_seats + 1)
            trip.booked_seats += 1
        if method:
            Payment.objects.create(
                booking=b, company=trip.company, user=user, amount=fare,
                payment_reference=f"PAY{uuid.uuid4().hex[:14].upper()}",
                payment_method="CASH" if method == "CASH" else "MOBILE_MONEY", status="COMPLETED",
                mobile_money_provider="" if method == "CASH" else method.title(),
                mobile_money_number="" if method == "CASH" else user.phone_number,
                gateway_transaction_id=f"SANDBOX-{b.booking_reference}", completed_at=timezone.now())
        return b
