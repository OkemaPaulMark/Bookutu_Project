from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.managers import TenantAwareManager
import uuid


User = get_user_model()


class Booking(models.Model):
    """
    Individual passenger bookings
    """
    BOOKING_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('MOBILE_APP', 'Mobile App'),
        ('WEB', 'Website'),
        ('DIRECT', 'Direct Booking'),
        ('PHONE', 'Phone Booking'),
        ('WALK_IN', 'Walk-in'),
    ]
    
    # Unique booking reference
    booking_reference = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relationships
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    seat = models.ForeignKey('companies.BusSeat', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Details
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='PENDING')
    source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='MOBILE_APP')
    
    # Passenger Information (stored for record keeping)
    passenger_name = models.CharField(max_length=200)
    passenger_phone = models.CharField(max_length=20)
    passenger_email = models.EmailField(blank=True)
    
    # Pricing
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    seat_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Booking Management
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bookings')  # Staff member who created direct booking
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    objects = TenantAwareManager()
    
    class Meta:
        db_table = 'bookings_booking'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['trip', 'status']),
            models.Index(fields=['passenger', 'status']),
            models.Index(fields=['booking_reference']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        
        # Ensure company consistency
        self.company = self.trip.company
        
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate unique booking reference"""
        prefix = "BK"
        timestamp = timezone.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"{prefix}{timestamp}{random_suffix}"
    
    def __str__(self):
        return f"{self.booking_reference} - {self.passenger_name}"
    
    def confirm_booking(self):
        """Confirm the booking"""
        self.status = 'CONFIRMED'
        self.confirmed_at = timezone.now()
        self.save()
        
        # Update trip booked seats count
        self.trip.booked_seats += 1
        self.trip.save()
    
    def cancel_booking(self, reason=""):
        """Cancel the booking"""
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.save()
        
        # Update trip booked seats count
        if self.trip.booked_seats > 0:
            self.trip.booked_seats -= 1
            self.trip.save()
        
        # Create cancellation record
        BookingCancellation.objects.create(
            booking=self,
            reason=reason,
            cancelled_by=self.passenger
        )
    
    def calculate_cancellation_fee(self):
        """Calculate cancellation fee based on company policy"""
        company_settings = self.company.settings
        hours_until_departure = (
            timezone.datetime.combine(self.trip.departure_date, self.trip.departure_time) - 
            timezone.now()
        ).total_seconds() / 3600
        
        if hours_until_departure >= company_settings.cancellation_hours:
            return 0  # Free cancellation
        else:
            return self.total_amount * (company_settings.cancellation_fee_percentage / 100)


class BookingCancellation(models.Model):
    """
    Track booking cancellations
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings_cancellation'
        verbose_name = 'Booking Cancellation'
        verbose_name_plural = 'Booking Cancellations'
    
    def __str__(self):
        return f"Cancellation for {self.booking.booking_reference}"


class BookingHistory(models.Model):
    """
    Track all changes to bookings for audit purposes
    """
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('MODIFIED', 'Modified'),
        ('COMPLETED', 'Completed'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Store previous and new values for modifications
    previous_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings_history'
        verbose_name = 'Booking History'
        verbose_name_plural = 'Booking Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.action}"


class SeatReservation(models.Model):
    """
    Temporary seat reservations during booking process
    """
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='seat_reservations')
    seat = models.ForeignKey('companies.BusSeat', on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seat_reservations')
    
    # Reservation expires after 15 minutes
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings_seat_reservation'
        verbose_name = 'Seat Reservation'
        verbose_name_plural = 'Seat Reservations'
        unique_together = ['trip', 'seat']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Reservation: {self.trip} - Seat {self.seat.seat_number}"
