# Generated migration for bookutu app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(default='Bookutu', max_length=100)),
                ('platform_tagline', models.CharField(default='Bus Booking Platform', max_length=200)),
                ('platform_description', models.TextField(default='A comprehensive multi-tenant bus booking platform')),
                ('logo', models.ImageField(blank=True, upload_to='system/logos/')),
                ('favicon', models.ImageField(blank=True, upload_to='system/favicons/')),
                ('primary_color', models.CharField(default='#059669', max_length=7)),
                ('secondary_color', models.CharField(default='#10b981', max_length=7)),
                ('support_email', models.EmailField(default='support@bookutu.com', max_length=254)),
                ('support_phone', models.CharField(blank=True, max_length=20)),
                ('company_address', models.TextField(blank=True)),
                ('maintenance_mode', models.BooleanField(default=False)),
                ('maintenance_message', models.TextField(blank=True)),
                ('registration_enabled', models.BooleanField(default=True)),
                ('facebook_url', models.URLField(blank=True)),
                ('twitter_url', models.URLField(blank=True)),
                ('linkedin_url', models.URLField(blank=True)),
                ('terms_of_service', models.TextField(blank=True)),
                ('privacy_policy', models.TextField(blank=True)),
                ('welcome_message', models.TextField(default='Welcome to our bus booking platform!')),
                ('booking_confirmation_message', models.TextField(default='Your booking has been confirmed.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'System Settings',
                'verbose_name_plural': 'System Settings',
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('announcement_type', models.CharField(choices=[('INFO', 'Information'), ('WARNING', 'Warning'), ('SUCCESS', 'Success'), ('ERROR', 'Error')], default='INFO', max_length=10)),
                ('show_to_passengers', models.BooleanField(default=True)),
                ('show_to_company_staff', models.BooleanField(default=True)),
                ('show_to_super_admin', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'ordering': ['-created_at'],
            },
        ),
    ]