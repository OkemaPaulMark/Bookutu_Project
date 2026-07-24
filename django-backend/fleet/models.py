from django.db import models

from common.enums import BusStatus
from common.ids import generate_id
from common.models import TimeStampedModel


class Bus(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='buses')
    license_plate = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=120)
    make = models.CharField(max_length=120)
    year = models.IntegerField()
    total_seats = models.IntegerField()
    bus_type = models.CharField(max_length=120)
    has_ac = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    has_charging_ports = models.BooleanField(default=False)
    has_entertainment = models.BooleanField(default=False)
    has_restroom = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=BusStatus.choices, default=BusStatus.ACTIVE)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'buses'
        ordering = ['-created_at']


class BusSeat(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=20)
    row_number = models.IntegerField()
    seat_position = models.CharField(max_length=20)
    seat_type = models.CharField(max_length=50)
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    has_extra_legroom = models.BooleanField(default=False)
    price_multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)

    class Meta:
        db_table = 'bus_seats'
        unique_together = ('bus', 'seat_number')


class Driver(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='drivers')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=120, unique=True)
    license_expiry_date = models.DateTimeField()
    date_of_birth = models.DateTimeField()
    employee_id = models.CharField(max_length=120, blank=True, null=True)
    hire_date = models.DateTimeField()
    status = models.CharField(max_length=32, default='ACTIVE')

    class Meta:
        db_table = 'drivers'
        ordering = ['-created_at']


class Route(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=255)
    origin_city = models.CharField(max_length=120)
    origin_terminal = models.CharField(max_length=120)
    destination_city = models.CharField(max_length=120)
    destination_terminal = models.CharField(max_length=120)
    distance_km = models.IntegerField()
    estimated_duration_hours = models.DecimalField(max_digits=8, decimal_places=2)
    base_fare = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    intermediate_stops = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'routes'
        ordering = ['-created_at']
