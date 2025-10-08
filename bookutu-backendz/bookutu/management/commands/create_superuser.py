from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with full admin rights'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Superuser email')
        parser.add_argument('--password', type=str, help='Superuser password')
        parser.add_argument('--first_name', type=str, help='First name', default='Admin')
        parser.add_argument('--last_name', type=str, help='Last name', default='User')

    def handle(self, *args, **options):
        email = options.get('email') or 'admin@bookutu.com'
        password = options.get('password') or 'admin123'
        first_name = options.get('first_name')
        last_name = options.get('last_name')

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser with email {email} already exists')
            )
            return

        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='SUPER_ADMIN'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser created successfully: {email}')
        )
        self.stdout.write(f'Password: {password}')
        self.stdout.write('Login at: http://127.0.0.1:8000/django-admin/')
