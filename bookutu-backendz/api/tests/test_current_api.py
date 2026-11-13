"""
End-to-end tests for the mobile API and dashboards as they work today.
These gate the CI/CD pipeline: nothing deploys to production unless they pass.

    python manage.py test api.tests.test_current_api
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from bookings.models import Booking
from companies.models import Bus, Company
from trips.models import Route, Trip
from trips.tasks import advance_trip_statuses

PASSWORD = "Str0ng!Passw0rd"


def make_company(slug="testco"):
    return Company.objects.create(
        name=f"{slug.title()} Coaches", slug=slug, email=f"info@{slug}.ug", phone_number="+256700000000",
        address="Kampala", city="Kampala", state="Central", registration_number=f"REG-{slug}",
        license_number=f"LIC-{slug}", status="ACTIVE")


def make_trip(company, days_ahead=2, dep="08:00", arr="13:00", status="SCHEDULED", plate="UAA 001A"):
    route, _ = Route.objects.get_or_create(
        company=company, origin_city="Kampala", destination_city="Gulu",
        defaults=dict(name="Kampala to Gulu", origin_terminal="Namayiba", destination_terminal="Gulu Park",
                      distance_km=340, estimated_duration_hours=5, base_fare=40000))
    bus = Bus.objects.create(company=company, license_plate=plate, model="KLQ", make="Higer", year=2022,
                             total_seats=12, bus_type="STANDARD", status="ACTIVE")
    return Trip.objects.create(company=company, route=route, bus=bus,
                               departure_date=timezone.localdate() + timedelta(days=days_ahead),
                               departure_time=dep, arrival_time=arr, base_fare=40000,
                               status=status, available_seats=12)


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_then_login_with_email(self):
        r = self.client.post("/api/auth/register/", {
            "first_name": "Amina", "last_name": "Nakato", "email": "amina@example.com",
            "phone_number": "+256701000000", "password": PASSWORD, "confirm_password": PASSWORD,
        }, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post("/api/auth/login/", {"email": "amina@example.com", "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIn("access", r.data)
        self.assertEqual(r.data["user"]["first_name"], "Amina")

    def test_wrong_password_rejected(self):
        User.objects.create_user(email="x@example.com", password=PASSWORD, user_type="PASSENGER")
        r = self.client.post("/api/auth/login/", {"email": "x@example.com", "password": "nope"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email="dup@example.com", password=PASSWORD, user_type="PASSENGER")
        r = self.client.post("/api/auth/register/", {
            "first_name": "A", "last_name": "B", "email": "dup@example.com", "phone_number": "+256700000001",
            "password": PASSWORD, "confirm_password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("email", r.data)

    def test_token_refresh(self):
        User.objects.create_user(email="r@example.com", password=PASSWORD, user_type="PASSENGER")
        login = self.client.post("/api/auth/login/", {"email": "r@example.com", "password": PASSWORD}, format="json")
        r = self.client.post("/api/auth/token/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)


class BookingFlowTests(TestCase):
    def setUp(self):
        self.company = make_company()
        self.trip = make_trip(self.company)
        self.user = User.objects.create_user(email="p@example.com", password=PASSWORD, first_name="Pat",
                                             phone_number="+256702000000", user_type="PASSENGER")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_trip_list_and_seat_map(self):
        trips = self.client.get("/api/auth/trips/").json()
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]["seats_left"], 12)
        seats = self.client.get(f"/api/auth/trips/{self.trip.id}/").json()["seats"]
        self.assertEqual(len(seats), 12)
        self.assertTrue(all(s["is_available"] for s in seats))

    def test_book_pay_cancel_rebook(self):
        r = self.client.post("/api/auth/bookings/create/",
                             {"trip": self.trip.id, "seat_numbers": ["1A", "1B"]}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        ids = [b["id"] for b in r.data["bookings"]]
        self.assertEqual({b["status"] for b in r.data["bookings"]}, {"PENDING"})

        # same seat can't be sold twice
        r = self.client.post("/api/auth/bookings/create/",
                             {"trip": self.trip.id, "seat_numbers": ["1A"]}, format="json")
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/auth/bookings/pay/",
                             {"booking_ids": ids, "method": "MTN", "phone": "0772000000"}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual({b["status"] for b in r.data["bookings"]}, {"CONFIRMED"})
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.booked_seats, 2)

        r = self.client.post(f"/api/auth/bookings/{ids[0]}/cancel/")
        self.assertEqual(r.status_code, 200, r.data)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.booked_seats, 1)

        # the cancelled seat is bookable again
        r = self.client.post("/api/auth/bookings/create/",
                             {"trip": self.trip.id, "seat_numbers": ["1A"]}, format="json")
        self.assertEqual(r.status_code, 201, r.data)

    def test_bookings_require_login(self):
        r = APIClient().post("/api/auth/bookings/create/",
                             {"trip": self.trip.id, "seat_numbers": ["1A"]}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_my_bookings_and_notifications(self):
        self.client.post("/api/auth/bookings/create/", {"trip": self.trip.id, "seat_numbers": ["2A"]}, format="json")
        mine = self.client.get("/api/auth/bookings/").json()
        self.assertEqual(mine["count"], 1)
        notes = self.client.get("/api/auth/notifications/").json()["notifications"]
        self.assertTrue(any(n["type"] == "booking" for n in notes))


class TripLifecycleTests(TestCase):
    def test_statuses_advance_and_map_shows_moving_bus(self):
        company = make_company("lifeco")
        now = timezone.localtime()
        if now.hour < 2 or now.hour > 21:
            self.skipTest("needs a same-day window around the current time")
        dep = (now - timedelta(hours=1)).time().replace(second=0, microsecond=0)
        arr = (now + timedelta(hours=1)).time().replace(second=0, microsecond=0)
        live = make_trip(company, days_ahead=0, dep=dep, arr=arr, plate="UAA 002B")
        done = make_trip(company, days_ahead=-1, plate="UAA 003C")
        rider = User.objects.create_user(email="rider@example.com", password=PASSWORD, user_type="PASSENGER")
        Booking.objects.create(company=company, trip=done, seat=done.bus.seats.first(), status="CONFIRMED",
                               passenger=rider,
                               passenger_name="X", passenger_phone="1", base_fare=1, total_amount=1)

        result = advance_trip_statuses()
        live.refresh_from_db(); done.refresh_from_db()
        self.assertEqual(live.status, "IN_TRANSIT")
        self.assertEqual(done.status, "COMPLETED")
        self.assertEqual(done.bookings.get().status, "COMPLETED")
        self.assertGreaterEqual(result["completed"], 1)

        buses = APIClient().get("/api/auth/map/").json()["buses"]
        self.assertEqual([b["state"] for b in buses if b["trip_id"] == live.id], ["IN_TRANSIT"])


class DashboardTests(TestCase):
    def setUp(self):
        self.company = make_company("dashco")
        self.trip = make_trip(self.company)
        self.staff = User.objects.create_user(email="staff@dashco.ug", password=PASSWORD,
                                              user_type="COMPANY_STAFF", company=self.company)
        self.admin = User.objects.create_superuser(email="root@bookutu.ug", password=PASSWORD)

    def test_company_pages_load(self):
        self.client.force_login(self.staff)
        for url in ["/company/", "/company/bookings/", "/company/fleet/", "/company/routes/",
                    "/company/trips/", "/company/drivers/", "/company/reports/", "/company/settings/",
                    f"/company/trips/{self.trip.id}/", f"/company/trips/{self.trip.id}/manifest/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_admin_pages_load_and_settings_save(self):
        self.client.force_login(self.admin)
        for url in ["/admin/", "/admin/companies/", "/admin/bookings/", "/admin/financials/",
                    "/admin/settings/", "/admin/adverts/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        r = self.client.post("/admin/settings/", {
            "platform_name": "Bookutu", "platform_tagline": "Tested", "support_email": "s@bookutu.com",
            "support_phone": "+256700000000", "default_commission_rate": "10.00", "currency": "UGX"})
        self.assertEqual(r.status_code, 302)

    def test_password_reset_page(self):
        self.assertEqual(self.client.get("/accounts/password-reset/").status_code, 200)
