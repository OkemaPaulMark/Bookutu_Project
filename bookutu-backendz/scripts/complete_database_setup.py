#!/usr/bin/env python
"""
Complete database setup script for Bookutu platform
This script sets up the entire database with all necessary data for CRUD operations
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookutu.settings')
django.setup()

def run_migrations():
    """Run all Django migrations"""
    print("🔄 Running Django migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
    execute_from_command_line(['manage.py', 'makemigrations', 'companies'])
    execute_from_command_line(['manage.py', 'makemigrations', 'trips'])
    execute_from_command_line(['manage.py', 'makemigrations', 'bookings'])
    execute_from_command_line(['manage.py', 'makemigrations', 'payments'])
    execute_from_command_line(['manage.py', 'makemigrations', 'notifications'])
    execute_from_command_line(['manage.py', 'makemigrations', 'bookutu'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrations completed")

def create_system_settings():
    """Create system settings"""
    from bookutu.models import SystemSettings
    
    settings = SystemSettings.get_settings()
    print("✅ System settings initialized")

def create_superuser():
    """Create initial superuser"""
    User = get_user_model()
    
    if not User.objects.filter(email='admin@bookutu.com').exists():
        print("👑 Creating superuser...")
        User.objects.create_superuser(
            email='admin@bookutu.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            phone_number='+256700000000',
            user_type='SUPER_ADMIN'
        )
        print("✅ Superuser created: admin@bookutu.com / admin123")
    else:
        print("✅ Superuser already exists")

def create_sample_companies():
    """Create sample bus companies with complete data"""
    from companies.models import Company, CompanySettings, Bus, BusSeat, Driver
    
    companies_data = [
        {
            'name': 'Swift Safaris',
            'slug': 'swift-safaris',
            'email': 'info@swiftsafaris.ug',
            'phone_number': '+256701234567',
            'address': 'Plot 15, Kampala Road, Kampala',
            'city': 'Kampala',
            'state': 'Central',
            'registration_number': 'SS001UG',
            'license_number': 'BL001SS',
            'status': 'ACTIVE'
        },
        {
            'name': 'Post Bus Uganda',
            'slug': 'post-bus',
            'email': 'contact@postbus.ug',
            'phone_number': '+256702345678',
            'address': 'Speke Road, Kampala',
            'city': 'Kampala',
            'state': 'Central',
            'registration_number': 'PB002UG',
            'license_number': 'BL002PB',
            'status': 'ACTIVE'
        },
        {
            'name': 'Jaguar Executive',
            'slug': 'jaguar-executive',
            'email': 'info@jaguarexec.ug',
            'phone_number': '+256703456789',
            'address': 'Entebbe Road, Kampala',
            'city': 'Kampala',
            'state': 'Central',
            'registration_number': 'JE003UG',
            'license_number': 'BL003JE',
            'status': 'ACTIVE'
        }
    ]
    
    for company_data in companies_data:
        company, created = Company.objects.get_or_create(
            slug=company_data['slug'],
            defaults=company_data
        )
        
        if created:
            # Create company settings
            CompanySettings.objects.create(company=company)
            
            # Create sample buses for each company
            create_sample_buses(company)
            
            # Create sample drivers
            create_sample_drivers(company)
            
            print(f"✅ Created company: {company.name}")

def create_sample_buses(company):
    """Create sample buses for a company"""
    from companies.models import Bus, BusSeat
    
    buses_data = [
        {
            'license_plate': f'{company.slug.upper()}-001',
            'registration_number': f'{company.slug.upper()}-REG-001',
            'model': 'Coaster',
            'make': 'Toyota',
            'manufacturer': 'Toyota',
            'year': 2020,
            'total_seats': 30,
            'bus_type': 'STANDARD'
        },
        {
            'license_plate': f'{company.slug.upper()}-002',
            'registration_number': f'{company.slug.upper()}-REG-002',
            'model': 'Sprinter',
            'make': 'Mercedes',
            'manufacturer': 'Mercedes-Benz',
            'year': 2021,
            'total_seats': 20,
            'bus_type': 'LUXURY'
        }
    ]
    
    for bus_data in buses_data:
        bus_data['company'] = company
        bus, created = Bus.objects.get_or_create(
            license_plate=bus_data['license_plate'],
            defaults=bus_data
        )
        
        if created:
            # Create seats for the bus
            create_bus_seats(bus)

def create_bus_seats(bus):
    """Create seats for a bus"""
    from companies.models import BusSeat
    
    seats_per_row = 4 if bus.total_seats > 25 else 3
    rows = (bus.total_seats + seats_per_row - 1) // seats_per_row
    
    seat_positions = ['A', 'B', 'C', 'D'] if seats_per_row == 4 else ['A', 'B', 'C']
    
    for row in range(1, rows + 1):
        for i, position in enumerate(seat_positions):
            if (row - 1) * seats_per_row + i + 1 <= bus.total_seats:
                BusSeat.objects.create(
                    bus=bus,
                    seat_number=f"{row}{position}",
                    row_number=row,
                    seat_position=position,
                    is_window=(i == 0 or i == seats_per_row - 1),
                    is_aisle=(i == 1 or i == 2) if seats_per_row == 4 else (i == 1)
                )

def create_sample_drivers(company):
    """Create sample drivers for a company"""
    from companies.models import Driver
    
    drivers_data = [
        {
            'first_name': 'John',
            'last_name': 'Mukasa',
            'phone_number': '+256711111111',
            'license_number': f'DL{company.id}001',
            'license_expiry_date': timezone.now().date().replace(year=2025),
            'date_of_birth': timezone.now().date().replace(year=1985),
            'hire_date': timezone.now().date()
        },
        {
            'first_name': 'Mary',
            'last_name': 'Nakato',
            'phone_number': '+256722222222',
            'license_number': f'DL{company.id}002',
            'license_expiry_date': timezone.now().date().replace(year=2025),
            'date_of_birth': timezone.now().date().replace(year=1990),
            'hire_date': timezone.now().date()
        }
    ]
    
    for driver_data in drivers_data:
        driver_data['company'] = company
        Driver.objects.get_or_create(
            license_number=driver_data['license_number'],
            defaults=driver_data
        )

def create_company_staff():
    """Create company staff users"""
    User = get_user_model()
    from companies.models import Company
    
    companies = Company.objects.all()
    
    for company in companies:
        email = f'admin@{company.slug}.ug'
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(
                email=email,
                password='staff123',
                first_name='Company',
                last_name='Admin',
                phone_number=f'+25670{company.id}000000',
                user_type='COMPANY_STAFF',
                company=company,
                is_verified=True
            )
            print(f"✅ Created staff user: {email}")

def create_sample_routes():
    """Create sample routes"""
    from trips.models import Route
    from companies.models import Company
    
    routes_data = [
        {
            'name': 'Kampala to Mbarara Express',
            'origin_city': 'Kampala',
            'origin_terminal': 'New Taxi Park',
            'destination_city': 'Mbarara',
            'destination_terminal': 'Mbarara Bus Terminal',
            'distance_km': 290,
            'estimated_duration_hours': Decimal('4.5'),
            'base_fare': Decimal('25000')
        },
        {
            'name': 'Kampala to Gulu Highway',
            'origin_city': 'Kampala',
            'origin_terminal': 'New Taxi Park',
            'destination_city': 'Gulu',
            'destination_terminal': 'Gulu Main Station',
            'distance_km': 340,
            'estimated_duration_hours': Decimal('5.0'),
            'base_fare': Decimal('30000')
        },
        {
            'name': 'Kampala to Jinja Express',
            'origin_city': 'Kampala',
            'origin_terminal': 'New Taxi Park',
            'destination_city': 'Jinja',
            'destination_terminal': 'Jinja Bus Park',
            'distance_km': 87,
            'estimated_duration_hours': Decimal('1.5'),
            'base_fare': Decimal('15000')
        }
    ]
    
    companies = Company.objects.all()
    
    for company in companies:
        for route_data in routes_data:
            route_data['company'] = company
            Route.objects.get_or_create(
                company=company,
                origin_city=route_data['origin_city'],
                destination_city=route_data['destination_city'],
                defaults=route_data
            )

def create_sample_trips():
    """Create sample trips"""
    from trips.models import Trip, Route
    from companies.models import Bus, Driver
    from datetime import datetime, timedelta
    
    routes = Route.objects.all()
    
    for route in routes:
        buses = Bus.objects.filter(company=route.company)
        drivers = Driver.objects.filter(company=route.company)
        
        if buses.exists() and drivers.exists():
            bus = buses.first()
            driver = drivers.first()
            
            # Create trips for next 7 days
            for i in range(7):
                trip_date = timezone.now().date() + timedelta(days=i)
                
                Trip.objects.get_or_create(
                    company=route.company,
                    route=route,
                    bus=bus,
                    departure_date=trip_date,
                    departure_time=datetime.strptime('08:00', '%H:%M').time(),
                    defaults={
                        'arrival_time': datetime.strptime('13:00', '%H:%M').time(),
                        'base_fare': route.base_fare,
                        'available_seats': bus.total_seats,
                        'driver_name': driver.full_name,
                        'driver_phone': driver.phone_number
                    }
                )

def create_sample_announcements():
    """Create sample system announcements"""
    from notifications.models import Announcement
    User = get_user_model()
    
    admin_user = User.objects.filter(user_type='SUPER_ADMIN').first()
    
    if admin_user:
        announcements_data = [
            {
                'title': 'Welcome to Bookutu Platform',
                'message': 'Welcome to the Bookutu bus booking platform. Book your tickets easily and travel safely.',
                'priority': 'medium',
                'target_audience': 'all'
            },
            {
                'title': 'New Routes Available',
                'message': 'We have added new routes to serve you better. Check out the latest destinations.',
                'priority': 'low',
                'target_audience': 'all'
            }
        ]
        
        for announcement_data in announcements_data:
            announcement_data['created_by'] = admin_user
            Announcement.objects.get_or_create(
                title=announcement_data['title'],
                defaults=announcement_data
            )

def create_indexes():
    """Create database indexes for better performance"""
    with connection.cursor() as cursor:
        indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON accounts_user(email);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_company ON accounts_user(company_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_status ON companies_company(status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_date ON trips_trip(departure_date);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_company ON trips_trip(company_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_trip ON bookings_booking(trip_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_status ON bookings_booking(status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_booking ON payments_payment(booking_id);"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"Index creation warning: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up complete Bookutu database...")
    
    try:
        with transaction.atomic():
            run_migrations()
            create_system_settings()
            create_superuser()
            create_sample_companies()
            create_company_staff()
            create_sample_routes()
            create_sample_trips()
            create_sample_announcements()
        
        create_indexes()
        
        print("\n🎉 Complete database setup completed successfully!")
        print("\n📊 Database Summary:")
        print("=" * 50)
        
        # Print summary
        User = get_user_model()
        from companies.models import Company, Bus, Driver
        from trips.models import Route, Trip
        from notifications.models import Announcement
        
        print(f"👥 Users: {User.objects.count()}")
        print(f"🏢 Companies: {Company.objects.count()}")
        print(f"🚌 Buses: {Bus.objects.count()}")
        print(f"👨‍✈️ Drivers: {Driver.objects.count()}")
        print(f"🛣️ Routes: {Route.objects.count()}")
        print(f"🎫 Trips: {Trip.objects.count()}")
        print(f"📢 Announcements: {Announcement.objects.count()}")
        
        print("\n🔑 Login Credentials:")
        print("=" * 30)
        print("Super Admin: admin@bookutu.com / admin123")
        print("Company Staff: admin@swift-safaris.ug / staff123")
        print("Company Staff: admin@post-bus.ug / staff123")
        print("Company Staff: admin@jaguar-executive.ug / staff123")
        
        print("\n🌐 Next Steps:")
        print("1. Start server: python manage.py runserver")
        print("2. Visit: http://localhost:8000/accounts/login/")
        print("3. API Docs: http://localhost:8000/api/docs/")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()