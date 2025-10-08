#!/usr/bin/env python
"""
Database setup script for Bookutu platform
Run this after creating your Django project to set up the database
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookutu.settings')
django.setup()

def run_migrations():
    """Run Django migrations"""
    print("Running Django migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    execute_from_command_line(['manage.py', 'migrate', 'bookutu'])
    print("✅ Migrations completed")

def create_superuser():
    """Create initial superuser"""
    User = get_user_model()
    
    if not User.objects.filter(email='admin@bookutu.com').exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            email='admin@bookutu.com',
            password='admin123',  # Change this!
            first_name='Super',
            last_name='Admin',
            phone_number='+256700000000',
            user_type='SUPER_ADMIN'
        )
        print("✅ Superuser created: admin@bookutu.com / admin123")
        print("⚠️  Please change the default password!")
    else:
        print("✅ Superuser already exists")

def run_sql_scripts():
    """Run SQL setup scripts"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    sql_files = [
        '01_initial_setup.sql',
        '02_seed_data.sql'
    ]
    
    with connection.cursor() as cursor:
        for sql_file in sql_files:
            file_path = os.path.join(script_dir, sql_file)
            if os.path.exists(file_path):
                print(f"Running {sql_file}...")
                with open(file_path, 'r') as f:
                    sql_content = f.read()
                    # Split by statements and execute
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    for statement in statements:
                        if statement and not statement.startswith('--'):
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                print(f"Warning: {e}")
                print(f"✅ {sql_file} completed")

def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✅ Static files collected")

def init_system_settings():
    """Initialize system settings"""
    print("Initializing system settings...")
    execute_from_command_line(['manage.py', 'init_system_settings'])
    print("✅ System settings initialized")

def main():
    """Main setup function"""
    print("🚀 Setting up Bookutu database...")
    
    try:
        run_migrations()
        create_superuser()
        init_system_settings()
        run_sql_scripts()
        collect_static()
        
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Update your .env file with proper database credentials")
        print("2. Change the default superuser password")
        print("3. Configure email and SMS settings")
        print("4. Start the development server: python manage.py runserver")
        print("5. Visit http://localhost:8000/api/docs/ for API documentation")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
