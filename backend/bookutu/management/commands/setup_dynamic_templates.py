from django.core.management.base import BaseCommand
from django.core.management import call_command
from bookutu.models import SystemSettings


class Command(BaseCommand):
    help = 'Setup dynamic templates system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up dynamic templates system...')
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', 'bookutu', verbosity=0)
        
        # Initialize system settings
        self.stdout.write('Initializing system settings...')
        settings, created = SystemSettings.objects.get_or_create(pk=1)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ System settings created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  System settings already exist')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Dynamic templates system is ready!')
        )
        self.stdout.write(f'Platform Name: {settings.platform_name}')
        self.stdout.write(f'Platform Tagline: {settings.platform_tagline}')
        self.stdout.write(f'Primary Color: {settings.primary_color}')
        self.stdout.write(f'Secondary Color: {settings.secondary_color}')