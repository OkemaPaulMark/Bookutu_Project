from django.core.management.base import BaseCommand
from bookutu.models import SystemSettings


class Command(BaseCommand):
    help = 'Initialize system settings with default values'

    def handle(self, *args, **options):
        settings, created = SystemSettings.objects.get_or_create(pk=1)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created default system settings')
            )
        else:
            self.stdout.write(
                self.style.WARNING('System settings already exist')
            )
        
        self.stdout.write(f'Platform Name: {settings.platform_name}')
        self.stdout.write(f'Platform Tagline: {settings.platform_tagline}')
        self.stdout.write(f'Support Email: {settings.support_email}')