from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



class Feedback(models.Model):
    bus_company = models.ForeignKey('BusCompany', related_name='feedback', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class BusCompany(models.Model):
    name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BusModel(models.Model):
    name = models.CharField(max_length=100)
    number_of_seats = models.PositiveIntegerField(default=0)
    # 3 seater boolean
    is_three_seater = models.BooleanField(default=False)
    is_electric = models.BooleanField(default=False)
    year_of_manufacture = models.PositiveIntegerField(null=True, blank=True)



class Bus(models.Model):
    bus_company = models.ForeignKey(BusCompany, related_name='buses', on_delete=models.CASCADE)
    number_plate = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    model = models.ForeignKey(BusModel, related_name='model', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.number_plate
    

class Route(models.Model):
    bus_company = models.ForeignKey('BusCompany', related_name='routes', on_delete=models.CASCADE, null=True, blank=True)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    estimated_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.start_location} → {self.end_location}"

class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    days = models.CharField(max_length=20)  # e.g. "1,3,5" for Mon/Wed/Fri
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.route} on {self.departure_time.date()} @ {self.departure_time.time()}"
    
    

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, related_name='bookings', on_delete=models.CASCADE)
    seat_number = models.PositiveBigIntegerField()

    booking_date = models.DateTimeField(auto_now_add=True)
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=20)
    booked_by_admin = models.BooleanField(default=False)
    
    # Payment fields (merged from Payment model)
    PAYMENT_METHOD_CHOICES = [
        ("mobile_money", "Mobile Money"),
        ("card", "Card"),
        ("cash", "Cash"),
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    BOOKING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
        ("refunded", "Refunded"),
        ("no_show", "No Show"),
        ("redeemed", "Redeemed")
    ]
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ('trip', 'seat_number')
        constraints = [
            models.CheckConstraint(
                check=models.Q(status='confirmed', payment_status='paid') | ~models.Q(status='confirmed'),
                name='booking_confirmed_only_if_paid'
            )
        ]

    def __str__(self):
        return f"Booking for {self.passenger_name} - Seat {self.seat_number} on Trip {self.trip.id}"
        
    def save(self, *args, **kwargs):
        # Auto-confirm booking when payment is marked as paid
        if self.payment_status == "paid" and self.status == "pending":
            self.status = "confirmed"
        super().save(*args, **kwargs)
        
    def clean(self):
        super().clean()
        # Check seat number is within bus capacity
        if self.trip.bus.model.number_of_seats and self.seat_number > self.trip.bus.model.number_of_seats:
            raise ValidationError(f"Seat number must be less than or equal to the bus capacity ({self.trip.bus.model.number_of_seats}).")
        # Check seat is not already booked for this trip
        if Booking.objects.filter(trip=self.trip, seat_number=self.seat_number).exclude(pk=self.pk).exists():
            raise ValidationError(f"Seat number {self.seat_number} is already booked for this trip.")
        # Ensure booking can only be confirmed if payment is successful
        if self.status == "confirmed" and self.payment_status != "paid":
            raise ValidationError("Booking cannot be confirmed until payment is successful.")
    
    
