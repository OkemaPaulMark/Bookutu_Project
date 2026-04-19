from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from companies.models import Company, Bus, BusSeat
from trips.models import Route, Trip
from bookings.models import Booking

User = get_user_model()


class MobileBookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Company
        self.company = Company.objects.create(
            name="Test Bus Co",
            slug="test-bus-co",
            description="",
            email="company@example.com",
            phone_number="0700000000",
            address="Address",
            city="Kampala",
            state="Central",
            country="Uganda",
            postal_code="",
            registration_number="REG123",
            license_number="LIC123",
        )
        # User (must be company staff per current User model)
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass1234",
            first_name="Test",
            last_name="User",
            phone_number="0700000001",
            user_type="COMPANY_STAFF",
            company=self.company,
        )
        self.client.force_authenticate(user=self.user)

        # Bus and seats
        self.bus = Bus.objects.create(
            company=self.company,
            license_plate="UAA000A",
            model="Model X",
            make="Make Y",
            year=2020,
            total_seats=4,
        )
        # Create 4 seats (2x2)
        self.seat1 = BusSeat.objects.create(
            bus=self.bus, seat_number="1A", row_number=1, seat_position="LEFT"
        )
        self.seat2 = BusSeat.objects.create(
            bus=self.bus, seat_number="1B", row_number=1, seat_position="RIGHT"
        )
        self.seat3 = BusSeat.objects.create(
            bus=self.bus, seat_number="2A", row_number=2, seat_position="LEFT"
        )
        self.seat4 = BusSeat.objects.create(
            bus=self.bus, seat_number="2B", row_number=2, seat_position="RIGHT"
        )

        # Route and trip (future date)
        self.route = Route.objects.create(
            company=self.company,
            name="KLA-GUL",
            origin_city="Kampala",
            origin_terminal="Park",
            destination_city="Gulu",
            destination_terminal="Main",
            distance_km=350,
            estimated_duration_hours=6.0,
            base_fare=20000,
        )
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        self.trip = Trip.objects.create(
            company=self.company,
            route=self.route,
            bus=self.bus,
            departure_date=tomorrow.date(),
            departure_time=(tomorrow + timezone.timedelta(hours=2)).time(),
            arrival_time=(tomorrow + timezone.timedelta(hours=8)).time(),
            base_fare=20000,
            available_seats=self.bus.total_seats,
        )

    def test_create_booking_success(self):
        url = "/api/mobile/bookings/create/"
        payload = {
            "trip": self.trip.id,
            "seat": self.seat1.id,
            "passenger_name": "Alice",
            "passenger_phone": "0700000010",
            "passenger_email": "alice@example.com",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        data = res.json()["booking"]
        self.assertEqual(data["status"], "PENDING")
        self.assertEqual(data["seat_info"]["seat_number"], "1A")
        self.assertTrue(
            Booking.objects.filter(trip=self.trip, seat=self.seat1).exists()
        )

    def test_create_booking_seat_already_booked(self):
        # Create an existing booking PENDING
        Booking.objects.create(
            company=self.company,
            trip=self.trip,
            passenger=self.user,
            seat=self.seat2,
            status="PENDING",
            source="MOBILE_APP",
            passenger_name="Bob",
            passenger_phone="0700000020",
            passenger_email="bob@example.com",
            base_fare=self.trip.base_fare,
            seat_fee=0,
            service_fee=0,
            total_amount=self.trip.base_fare,
        )
        url = "/api/mobile/bookings/create/"
        payload = {
            "trip": self.trip.id,
            "seat": self.seat2.id,
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_booking_invalid_seat_for_bus(self):
        # Create another bus with a seat not on the trip bus
        other_bus = Bus.objects.create(
            company=self.company,
            license_plate="UAA111A",
            model="Model Z",
            make="Make Y",
            year=2021,
            total_seats=1,
        )
        other_seat = BusSeat.objects.create(
            bus=other_bus, seat_number="1A", row_number=1, seat_position="LEFT"
        )
        url = "/api/mobile/bookings/create/"
        payload = {
            "trip": self.trip.id,
            "seat": other_seat.id,
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
