from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.managers import TenantAwareManager
from decimal import Decimal


class Route(models.Model):
    """
    Travel routes between cities/locations
    """
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='routes')
    
    # Route Information
    name = models.CharField(max_length=200)  # e.g., "Kampala to Gulu Express"
    origin_city = models.CharField(max_length=100)
    origin_terminal = models.CharField(max_length=200)
    destination_city = models.CharField(max_length=100)
    destination_terminal = models.CharField(max_length=200)
    
    # Route Details
    distance_km = models.PositiveIntegerField()
    estimated_duration_hours = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 5.5 hours
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Route Status
    is_active = models.BooleanField(default=True)
    
    # Intermediate stops (JSON field for flexibility)
    intermediate_stops = models.JSONField(default=list, blank=True)  # [{"city": "Lira", "duration_minutes": 30}]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantAwareManager()
    
    class Meta:
        db_table = 'trips_route'
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        unique_together = ['company', 'origin_city', 'destination_city']
        ordering = ['origin_city', 'destination_city']
    
    @property
    def origin(self):
        return self.origin_city
    
    @property
    def destination(self):
        return self.destination_city
    
    @property
    def distance(self):
        return self.distance_km
    
    @property
    def duration(self):
        return f"{self.estimated_duration_hours}h"
    
    def __str__(self):
        return f"{self.origin_city} → {self.destination_city}"


class Trip(models.Model):
    """
    Scheduled trips on specific routes
    """
    TRIP_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('BOARDING', 'Boarding'),
        ('IN_TRANSIT', 'In Transit'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('DELAYED', 'Delayed'),
    ]
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey('companies.Bus', on_delete=models.CASCADE, related_name='trips')
    
    # Trip Schedule
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    
    # Pricing
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Trip Status
    status = models.CharField(max_length=20, choices=TRIP_STATUS_CHOICES, default='SCHEDULED')
    actual_departure_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)
    
    # Capacity Management
    available_seats = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)
    
    # Driver Information
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    conductor_name = models.CharField(max_length=100, blank=True)
    conductor_phone = models.CharField(max_length=20, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantAwareManager()
    
    class Meta:
        db_table = 'trips_trip'
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        ordering = ['departure_date', 'departure_time']
        indexes = [
            models.Index(fields=['company', 'departure_date']),
            models.Index(fields=['route', 'departure_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.route} - {self.departure_date} {self.departure_time}"
    
    def clean(self):
        # Validate that bus belongs to the same company
        if self.bus and self.bus.company != self.company:
            raise ValidationError("Bus must belong to the same company as the trip")
        
        # Validate that route belongs to the same company
        if self.route and self.route.company != self.company:
            raise ValidationError("Route must belong to the same company as the trip")
        
        # Set available seats based on bus capacity
        if self.bus:
            self.available_seats = self.bus.total_seats
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def occupancy_percentage(self):
        if self.available_seats == 0:
            return 0
        return (self.booked_seats / self.available_seats) * 100
    
    @property
    def remaining_seats(self):
        return self.available_seats - self.booked_seats
    
    def is_bookable(self):
        """Check if trip is available for booking"""
        now = timezone.now()
        trip_datetime = timezone.make_aware(
            timezone.datetime.combine(self.departure_date, self.departure_time)
        )
        
        return (
            self.status == 'SCHEDULED' and
            trip_datetime > now and
            self.remaining_seats > 0
        )


class TripPricing(models.Model):
    """
    Dynamic pricing for trips based on various factors
    """
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='pricing')
    
    # Pricing Factors
    peak_season_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    demand_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    early_bird_discount = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Final Pricing
    final_base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Pricing Rules
    early_bird_days = models.PositiveIntegerField(default=7)  # Days before departure for early bird discount
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trips_pricing'
        verbose_name = 'Trip Pricing'
        verbose_name_plural = 'Trip Pricing'
    
    def calculate_final_fare(self, seat_type_multiplier=1.00):
        """Calculate final fare including all multipliers"""
        base = self.trip.base_fare
        
        # Apply all multipliers
        final_fare = base * self.peak_season_multiplier * self.demand_multiplier * Decimal(str(seat_type_multiplier))
        
        # Apply early bird discount if applicable
        days_until_departure = (self.trip.departure_date - timezone.now().date()).days
        if days_until_departure >= self.early_bird_days:
            final_fare = final_fare * (1 - self.early_bird_discount)
        
        return final_fare.quantize(Decimal('0.01'))
