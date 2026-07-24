from django.db import models

from common.ids import generate_id
from common.models import TimeStampedModel


class Trip(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey('fleet.Route', on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey('fleet.Bus', on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey('fleet.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    departure_date = models.DateTimeField()
    departure_time = models.CharField(max_length=20)
    arrival_time = models.CharField(max_length=20)
    base_fare = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=32, default='SCHEDULED')
    available_seats = models.IntegerField()
    booked_seats = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'trips'
        ordering = ['-created_at']


class TripPricing(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='pricing')
    peak_season_multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    demand_multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    early_bird_discount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    early_bird_days = models.IntegerField(default=7)
    final_base_fare = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'trip_pricing'
