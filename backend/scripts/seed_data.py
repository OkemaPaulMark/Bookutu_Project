#!/usr/bin/env python
"""
Seed data script for Bookutu platform
Creates sample companies, buses, routes, and other data for testing
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.db import connection
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookutu.settings')
django.setup()

from companies.models import Company, Bus, Driver, CompanySettings
from trips.models import Route, Trip
from bookings.models import Booking
from accounts.models import User

def create_sample_data():
    """Create sample data for testing"""
    print("🌱 Creating sample data...")
    
    # Create a sample company
    company, created = Company.objects.get_or_create(
        name="Swift Bus Services",
        defaults={
            'slug': 'swift-bus-services',
            'description': 'Reliable bus transportation services across Uganda',
            'email': 'info@swiftbus.com',
            'phone_number': '+256 700 123456',
            'website': 'https://swiftbus.com',
            'address': 'Kampala Road, Central Business District',
            'city': 'Kampala',
            'state': 'Central Region',
            'country': 'Uganda',
            'registration_number': 'REG-001-2023',
            'license_number': 'LIC-001-2023',
            'status': 'ACTIVE'
        }
    )
    
    if created:
        print(f"✅ Created company: {company.name}")
    else:
        print(f"✅ Using existing company: {company.name}")
    
    # Create company settings
    settings, created = CompanySettings.objects.get_or_create(
        company=company,
        defaults={
            'advance_booking_days': 30,
            'cancellation_hours': 24,
            'cancellation_fee_percentage': 10.00,
            'accepts_cash': True,
            'accepts_mobile_money': True,
            'accepts_card': True,
            'send_sms_notifications': True,
            'send_email_notifications': True,
            'office_open_time': '08:00',
            'office_close_time': '18:00',
        }
    )
    
    # Create company staff user
    staff_user, created = User.objects.get_or_create(
        email='staff@swiftbus.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Manager',
            'phone_number': '+256 700 123456',
            'user_type': 'COMPANY_STAFF',
            'company': company,
            'is_active': True,
            'is_verified': True
        }
    )
    
    if created:
        staff_user.set_password('staff123')
        staff_user.save()
        print(f"✅ Created staff user: {staff_user.email}")
    else:
        print(f"✅ Using existing staff user: {staff_user.email}")
    
    # Create sample buses
    buses_data = [
        {
            'license_plate': 'UG 1234A',
            'model': 'Coaster',
            'make': 'Toyota',
            'year': 2022,
            'total_seats': 28,
            'bus_type': 'STANDARD',
            'status': 'ACTIVE',
            'has_ac': True,
            'has_wifi': True,
            'has_charging_ports': True,
        },
        {
            'license_plate': 'UG 5678B',
            'model': 'Hiace X',
            'make': 'Toyota',
            'year': 2021,
            'total_seats': 14,
            'bus_type': 'LUXURY',
            'status': 'ACTIVE',
            'has_ac': True,
            'has_wifi': True,
            'has_charging_ports': True,
        },
        {
            'license_plate': 'UG 9012C',
            'model': 'Sprinter',
            'make': 'Mercedes',
            'year': 2023,
            'total_seats': 32,
            'bus_type': 'VIP',
            'status': 'MAINTENANCE',
            'has_ac': True,
            'has_wifi': True,
            'has_charging_ports': True,
            'has_entertainment': True,
        }
    ]
    
    for bus_data in buses_data:
        bus, created = Bus.objects.get_or_create(
            license_plate=bus_data['license_plate'],
            defaults={**bus_data, 'company': company}
        )
        if created:
            print(f"✅ Created bus: {bus.license_plate}")
        else:
            print(f"✅ Using existing bus: {bus.license_plate}")
    
    # Create sample drivers
    drivers_data = [
        {
            'first_name': 'John',
            'last_name': 'Mukasa',
            'phone_number': '+256 772 123456',
            'email': 'john.mukasa@swiftbus.com',
            'license_number': 'DL-123456789',
            'license_expiry_date': '2025-12-31',
            'date_of_birth': '1985-06-15',
            'employee_id': 'EMP001',
            'hire_date': '2020-01-15',
            'status': 'ACTIVE',
            'emergency_contact_name': 'Mary Mukasa',
            'emergency_contact_phone': '+256 700 987654',
        },
        {
            'first_name': 'Peter',
            'last_name': 'Kato',
            'phone_number': '+256 752 987654',
            'email': 'peter.kato@swiftbus.com',
            'license_number': 'DL-987654321',
            'license_expiry_date': '2026-03-15',
            'date_of_birth': '1980-03-22',
            'employee_id': 'EMP002',
            'hire_date': '2019-08-10',
            'status': 'ACTIVE',
            'emergency_contact_name': 'Grace Kato',
            'emergency_contact_phone': '+256 700 123789',
        }
    ]
    
    for driver_data in drivers_data:
        driver, created = Driver.objects.get_or_create(
            license_number=driver_data['license_number'],
            defaults={**driver_data, 'company': company}
        )
        if created:
            print(f"✅ Created driver: {driver.full_name}")
        else:
            print(f"✅ Using existing driver: {driver.full_name}")
    
    # Create sample routes
    routes_data = [
        {
            'name': 'Kampala to Gulu Express',
            'origin_city': 'Kampala',
            'origin_terminal': 'Kampala Bus Terminal',
            'destination_city': 'Gulu',
            'destination_terminal': 'Gulu Bus Terminal',
            'distance_km': 332,
            'estimated_duration_hours': 5.5,
            'base_fare': Decimal('35000.00'),
            'is_active': True,
            'intermediate_stops': [
                {"city": "Luwero", "duration_minutes": 30},
                {"city": "Nakasongola", "duration_minutes": 45}
            ]
        },
        {
            'name': 'Kampala to Mbarara Express',
            'origin_city': 'Kampala',
            'origin_terminal': 'Kampala Bus Terminal',
            'destination_city': 'Mbarara',
            'destination_terminal': 'Mbarara Bus Terminal',
            'distance_km': 266,
            'estimated_duration_hours': 4.25,
            'base_fare': Decimal('28000.00'),
            'is_active': True,
            'intermediate_stops': [
                {"city": "Masaka", "duration_minutes": 30},
                {"city": "Lyantonde", "duration_minutes": 20}
            ]
        },
        {
            'name': 'Kampala to Jinja Express',
            'origin_city': 'Kampala',
            'origin_terminal': 'Kampala Bus Terminal',
            'destination_city': 'Jinja',
            'destination_terminal': 'Jinja Bus Terminal',
            'distance_km': 80,
            'estimated_duration_hours': 1.5,
            'base_fare': Decimal('15000.00'),
            'is_active': True,
            'intermediate_stops': []
        }
    ]
    
    for route_data in routes_data:
        route, created = Route.objects.get_or_create(
            company=company,
            origin_city=route_data['origin_city'],
            destination_city=route_data['destination_city'],
            defaults=route_data
        )
        if created:
            print(f"✅ Created route: {route}")
        else:
            print(f"✅ Using existing route: {route}")
    
    # Create sample trips
    from datetime import date, time, timedelta
    import random
    
    buses = list(Bus.objects.filter(company=company, status='ACTIVE'))
    routes = list(Route.objects.filter(company=company, is_active=True))
    
    if buses and routes:
        # Create trips for the next 7 days
        for i in range(7):
            trip_date = date.today() + timedelta(days=i)
            
            for route in routes:
                # Create 2-3 trips per route per day
                for j in range(random.randint(2, 3)):
                    departure_time = time(hour=random.randint(6, 18), minute=random.choice([0, 30]))
                    bus = random.choice(buses)
                    
                    trip, created = Trip.objects.get_or_create(
                        company=company,
                        route=route,
                        bus=bus,
                        departure_date=trip_date,
                        departure_time=departure_time,
                        defaults={
                            'arrival_time': time(
                                hour=(departure_time.hour + int(route.estimated_duration_hours)) % 24,
                                minute=departure_time.minute
                            ),
                            'base_fare': route.base_fare,
                            'status': 'SCHEDULED',
                            'available_seats': bus.total_seats,
                            'booked_seats': random.randint(0, bus.total_seats // 2),
                            'driver_name': f"{random.choice(drivers_data)['first_name']} {random.choice(drivers_data)['last_name']}",
                            'driver_phone': random.choice(drivers_data)['phone_number'],
                        }
                    )
                    
                    if created:
                        print(f"✅ Created trip: {trip}")
    
    print("\n🎉 Sample data creation completed!")
    print("\nLogin credentials:")
    print("Staff User: staff@swiftbus.com / staff123")
    print("Super Admin: admin@bookutu.com / admin123")

def main():
    """Main function"""
    print("🚀 Seeding Bookutu database with sample data...")
    
    try:
        create_sample_data()
        
        print("\n✅ Database seeding completed successfully!")
        print("\nYou can now:")
        print("1. Start the development server: python manage.py runserver")
        print("2. Login with the sample credentials")
        print("3. Test the CRUD operations")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
