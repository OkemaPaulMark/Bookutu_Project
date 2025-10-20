import logging
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.managers import TenantAwareManager
from decimal import Decimal

logger = logging.getLogger(__name__)


class Route(models.Model):
    """
    Travel routes between cities/locations
    """

    company = models.ForeignKey(
        "companies.Company", on_delete=models.CASCADE, related_name="routes"
    )

    # Route Information
    name = models.CharField(max_length=200)  # e.g., "Kampala to Gulu Express"
    origin_city = models.CharField(max_length=100)
    origin_terminal = models.CharField(max_length=200)
    destination_city = models.CharField(max_length=100)
    destination_terminal = models.CharField(max_length=200)

    # Route Details
    distance_km = models.PositiveIntegerField()
    estimated_duration_hours = models.DecimalField(
        max_digits=4, decimal_places=2
    )  # e.g., 5.5 hours
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)

    # Route Status
    is_active = models.BooleanField(default=True)

    # Intermediate stops (JSON field for flexibility)
    intermediate_stops = models.JSONField(
        default=list, blank=True
    )  # [{"city": "Lira", "duration_minutes": 30}]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        db_table = "trips_route"
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        unique_together = ["company", "origin_city", "destination_city"]
        ordering = ["origin_city", "destination_city"]

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
        ("SCHEDULED", "Scheduled"),
        ("BOARDING", "Boarding"),
        ("IN_TRANSIT", "In Transit"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("DELAYED", "Delayed"),
    ]

    company = models.ForeignKey(
        "companies.Company", on_delete=models.CASCADE, related_name="trips"
    )
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    bus = models.ForeignKey(
        "companies.Bus", on_delete=models.CASCADE, related_name="trips"
    )

    # Trip Schedule
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    # Pricing
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)

    # Trip Status
    status = models.CharField(
        max_length=20, choices=TRIP_STATUS_CHOICES, default="SCHEDULED"
    )
    actual_departure_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)

    # Capacity Management
    available_seats = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)

    # Driver Information
    driver = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driven_trips",
        limit_choices_to={
            "user_type": "COMPANY_STAFF"
        },  # Assuming drivers are company staff
    )
    # The existing driver_name and driver_phone fields can be removed or kept for historical/denormalized data if needed.
    # For now, I'll keep them but they should ideally be derived from the driver User object.
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    driver_phone = models.CharField(max_length=20, blank=True, null=True)
    conductor_name = models.CharField(max_length=100, blank=True, null=True)
    conductor_phone = models.CharField(max_length=20, blank=True, null=True)

    # Notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        db_table = "trips_trip"
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ["departure_date", "departure_time"]
        indexes = [
            models.Index(fields=["company", "departure_date"]),
            models.Index(fields=["route", "departure_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.route} - {self.departure_date} {self.departure_time}"

    def clean(self):
        logger.info(f"Validating trip {self} for company {self.company}")

        # Validate that bus belongs to the same company
        if self.bus and self.bus.company != self.company:
            logger.error(
                f"Bus {self.bus} company {self.bus.company} != trip company {self.company}"
            )
            raise ValidationError("Bus must belong to the same company as the trip")

        # Validate that route belongs to the same company
        if self.route and self.route.company != self.company:
            logger.error(
                f"Route {self.route} company {self.route.company} != trip company {self.company}"
            )
            raise ValidationError("Route must belong to the same company as the trip")

        # Check for bus scheduling conflicts
        if (
            self.bus
            and self.departure_date
            and self.departure_time
            and self.arrival_time
        ):
            # Check if bus is already scheduled for another trip at overlapping time
            # A conflict occurs if:
            # - Another trip starts during this trip's duration
            # - Another trip ends during this trip's duration
            # - Another trip completely encompasses this trip
            conflicting_trips = (
                Trip.objects.filter(bus=self.bus, departure_date=self.departure_date)
                .exclude(pk=self.pk)
                .filter(
                    models.Q(
                        # Other trip starts during this trip
                        departure_time__gte=self.departure_time,
                        departure_time__lt=self.arrival_time,
                    )
                    | models.Q(
                        # Other trip ends during this trip
                        arrival_time__gt=self.departure_time,
                        arrival_time__lte=self.arrival_time,
                    )
                    | models.Q(
                        # Other trip encompasses this trip
                        departure_time__lte=self.departure_time,
                        arrival_time__gte=self.arrival_time,
                    )
                )
            )

            if conflicting_trips.exists():
                conflict_details = [
                    f"Trip {t.id}: {t.route.name} ({t.departure_time}-{t.arrival_time})"
                    for t in conflicting_trips
                ]
                logger.error(
                    f"Bus scheduling conflict for {self.bus} on {self.departure_date}: {conflict_details}"
                )
                raise ValidationError(
                    f"Bus {self.bus.license_plate} is already scheduled for conflicting trips: {', '.join(conflict_details)}"
                )

        # Validate departure before arrival
        if (
            self.departure_time
            and self.arrival_time
            and self.departure_time >= self.arrival_time
        ):
            logger.error(
                f"Trip {self} has invalid times: departure {self.departure_time} >= arrival {self.arrival_time}"
            )
            raise ValidationError("Arrival time must be after departure time")

        # Set available seats based on bus capacity if not already set (e.g., for new trips)
        # For existing trips, available_seats might be dynamically updated based on bookings.
        if self.bus and self.pk is None:  # Only set for new trips
            self.available_seats = self.bus.total_seats
            logger.info(
                f"Set initial available seats to {self.available_seats} for bus {self.bus}"
            )

        # If a driver is assigned, populate driver_name and driver_phone for convenience/denormalization
        if self.driver:
            self.driver_name = self.driver.get_full_name()
            self.driver_phone = self.driver.phone_number
        else:
            self.driver_name = None
            self.driver_phone = None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        logger.info(f"Saving trip {self} (new: {is_new})")

        self.clean()
        super().save(*args, **kwargs)

        # Create TripPricing if this is a new trip
        if is_new:
            TripPricing.objects.get_or_create(
                trip=self,
                defaults={
                    "peak_season_multiplier": 1.00,
                    "demand_multiplier": 1.00,
                    "early_bird_discount": 0.00,
                    "early_bird_days": 7,
                    "final_base_fare": self.base_fare,
                },
            )
            logger.info(f"Created TripPricing for new trip {self}")

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
            self.status == "SCHEDULED"
            and trip_datetime > now
            and self.remaining_seats > 0
        )


class TripPricing(models.Model):
    """
    Dynamic pricing for trips based on various factors
    """

    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name="pricing")

    # Pricing Factors
    peak_season_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.00
    )
    demand_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.00
    )
    early_bird_discount = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00
    )

    # Final Pricing
    final_base_fare = models.DecimalField(max_digits=10, decimal_places=2)

    # Pricing Rules
    early_bird_days = models.PositiveIntegerField(
        default=7
    )  # Days before departure for early bird discount

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trips_pricing"
        verbose_name = "Trip Pricing"
        verbose_name_plural = "Trip Pricing"

    def calculate_final_fare(self, seat_type_multiplier=1.00):
        """Calculate final fare including all multipliers"""
        base = self.trip.base_fare

        # Apply all multipliers
        final_fare = (
            base
            * self.peak_season_multiplier
            * self.demand_multiplier
            * Decimal(str(seat_type_multiplier))
        )

        # Apply early bird discount if applicable
        days_until_departure = (self.trip.departure_date - timezone.now().date()).days
        if days_until_departure >= self.early_bird_days:
            final_fare = final_fare * (1 - self.early_bird_discount)

        return final_fare.quantize(Decimal("0.01"))
