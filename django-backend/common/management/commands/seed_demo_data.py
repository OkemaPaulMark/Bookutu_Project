from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from adverts.models import Advert
from authentication.models import User
from common.enums import CompanyStatus, UserType
from companies.models import Company
from fleet.models import Bus, BusSeat, Driver, Route
from trips.models import Trip

SEAT_POSITIONS = ['LEFT_WINDOW', 'LEFT_AISLE', 'RIGHT_AISLE', 'RIGHT_WINDOW']
SEAT_LETTERS = ['A', 'B', 'C', 'D']


def _create_seats(bus, total_seats):
    if bus.seats.exists():
        return
    rows = (total_seats // 4)
    seats = []
    for row_index in range(rows):
        row_number = row_index + 1
        for i, letter in enumerate(SEAT_LETTERS):
            seats.append(BusSeat(
                bus=bus,
                seat_number=f'{row_number}{letter}',
                row_number=row_number,
                seat_position=SEAT_POSITIONS[i],
                seat_type='REGULAR',
                is_window=i in (0, 3),
                is_aisle=i in (1, 2),
                has_extra_legroom=False,
                price_multiplier=1,
            ))
    BusSeat.objects.bulk_create(seats)


class Command(BaseCommand):
    help = 'Seeds the database with demo companies, fleet, routes, trips, adverts, and passenger accounts for testing.'

    def handle(self, *args, **options):
        companies = self._seed_companies()
        for company in companies:
            buses = self._seed_buses(company)
            drivers = self._seed_drivers(company)
            routes = self._seed_routes(company)
            self._seed_trips(company, buses, drivers, routes)

        self._seed_adverts()
        self._seed_passengers()

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))

    def _seed_companies(self):
        specs = [
            dict(
                name='Kampala Coaches Ltd', slug='kampala-coaches-ltd',
                email='info@kampalacoaches.example', phone_number='0700111222',
                address='Old Taxi Park Rd', city='Kampala', state='Central',
                registration_number='REG-DEMO-001', license_number='LIC-DEMO-001',
                status=CompanyStatus.ACTIVE,
            ),
            dict(
                name='Pearl Bus Services', slug='pearl-bus-services',
                email='info@pearlbus.example', phone_number='0700333444',
                address='Jinja Rd', city='Jinja', state='Eastern',
                registration_number='REG-DEMO-002', license_number='LIC-DEMO-002',
                status=CompanyStatus.ACTIVE,
            ),
        ]
        companies = []
        for spec in specs:
            company, created = Company.objects.get_or_create(
                registration_number=spec['registration_number'],
                defaults=spec,
            )
            companies.append(company)
            self.stdout.write(f'{"Created" if created else "Reused"} company: {company.name}')
        return companies

    def _seed_buses(self, company):
        specs = [
            dict(license_plate=f'UAX-{company.id[:4].upper()}1', model='Coaster', make='Toyota', year=2021, total_seats=32, bus_type='STANDARD'),
            dict(license_plate=f'UAX-{company.id[:4].upper()}2', model='Marcopolo', make='Scania', year=2022, total_seats=48, bus_type='LUXURY', has_wifi=True, has_entertainment=True),
        ]
        buses = []
        for spec in specs:
            bus, created = Bus.objects.get_or_create(
                license_plate=spec['license_plate'],
                defaults={**spec, 'company': company},
            )
            _create_seats(bus, bus.total_seats)
            buses.append(bus)
            self.stdout.write(f'  {"Created" if created else "Reused"} bus: {bus.license_plate}')
        return buses

    def _seed_drivers(self, company):
        specs = [
            dict(first_name='Moses', last_name='Okello', phone_number='0701234567', license_number=f'DL-{company.id[:6]}-01'),
            dict(first_name='Grace', last_name='Namutebi', phone_number='0709876543', license_number=f'DL-{company.id[:6]}-02'),
        ]
        drivers = []
        for spec in specs:
            driver, created = Driver.objects.get_or_create(
                license_number=spec['license_number'],
                defaults={
                    **spec,
                    'company': company,
                    'license_expiry_date': timezone.now() + timedelta(days=365),
                    'date_of_birth': datetime(1988, 1, 1, tzinfo=timezone.get_current_timezone()),
                    'hire_date': timezone.now() - timedelta(days=180),
                    'status': 'ACTIVE',
                },
            )
            drivers.append(driver)
            self.stdout.write(f'  {"Created" if created else "Reused"} driver: {driver.first_name} {driver.last_name}')
        return drivers

    def _seed_routes(self, company):
        specs = [
            dict(name='Kampala - Gulu', origin_city='Kampala', origin_terminal='Old Taxi Park', destination_city='Gulu', destination_terminal='Gulu Main Park', distance_km=340, estimated_duration_hours=6, base_fare=45000),
            dict(name='Kampala - Mbarara', origin_city='Kampala', origin_terminal='Old Taxi Park', destination_city='Mbarara', destination_terminal='Mbarara Park', distance_km=270, estimated_duration_hours=4, base_fare=35000),
        ]
        routes = []
        for spec in specs:
            route, created = Route.objects.get_or_create(
                company=company, origin_city=spec['origin_city'], destination_city=spec['destination_city'],
                defaults={**spec, 'company': company},
            )
            routes.append(route)
            self.stdout.write(f'  {"Created" if created else "Reused"} route: {route.name}')
        return routes

    def _seed_trips(self, company, buses, drivers, routes):
        today = date.today()
        statuses_by_offset = {0: 'SCHEDULED', 1: 'SCHEDULED', 2: 'SCHEDULED', -1: 'COMPLETED', -2: 'COMPLETED'}

        created_count = 0
        for offset, status in statuses_by_offset.items():
            for i, route in enumerate(routes):
                bus = buses[i % len(buses)]
                driver = drivers[i % len(drivers)]
                departure_date = timezone.make_aware(
                    datetime.combine(today + timedelta(days=offset), datetime.min.time())
                )

                trip, created = Trip.objects.get_or_create(
                    company=company, route=route, bus=bus, departure_date=departure_date,
                    defaults=dict(
                        driver=driver,
                        departure_time='08:00',
                        arrival_time='14:00',
                        base_fare=route.base_fare,
                        status=status,
                        available_seats=bus.total_seats,
                        booked_seats=0,
                    ),
                )
                if created:
                    created_count += 1
        self.stdout.write(f'  Seeded {created_count} new trips for {company.name}')

    def _seed_adverts(self):
        specs = [
            dict(title='Independence Day Fare Discount', description='Get 15% off all upcountry routes this week.', image_url='https://picsum.photos/seed/bookutu1/400/300', link_url='https://bookutu.example.com/promo/independence'),
            dict(title='Refer a Friend, Ride Free', description='Invite a friend to Bookutu and earn a free ticket.', image_url='https://picsum.photos/seed/bookutu2/400/300', link_url='https://bookutu.example.com/promo/referral'),
            dict(title='New Route: Kampala - Gulu', description='Now booking the newest route with reclining seats and WiFi.', image_url='https://picsum.photos/seed/bookutu3/400/300', link_url=None),
        ]
        for spec in specs:
            advert, created = Advert.objects.get_or_create(title=spec['title'], defaults=spec)
            self.stdout.write(f'{"Created" if created else "Reused"} advert: {advert.title}')

    def _seed_passengers(self):
        specs = [
            dict(email='jane.doe@example.com', first_name='Jane', last_name='Doe', phone_number='0770111222'),
            dict(email='paul.mugisha@example.com', first_name='Paul', last_name='Mugisha', phone_number='0770333444'),
            dict(email='amina.nabirye@example.com', first_name='Amina', last_name='Nabirye', phone_number='0770555666'),
            dict(email='brian.okwir@example.com', first_name='Brian', last_name='Okwir', phone_number='0770777888'),
            dict(email='sarah.kamau@example.com', first_name='Sarah', last_name='Kamau', phone_number='0770999000'),
        ]
        for spec in specs:
            user, created = User.objects.get_or_create(
                email=spec['email'],
                defaults={**spec, 'user_type': UserType.PASSENGER, 'is_verified': True, 'is_active': True},
            )
            if created:
                user.set_password('passenger123')
                user.save(update_fields=['password'])
            self.stdout.write(f'{"Created" if created else "Reused"} passenger: {user.email}')
