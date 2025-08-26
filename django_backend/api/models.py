from django.db import models
from django.contrib.auth.models import User



class Feedback(models.Model):
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

class Bus(models.Model):
    company = models.ForeignKey(BusCompany, related_name='buses', on_delete=models.CASCADE)
    number_plate = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.number_plate
    
    
class Route(models.Model):
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
    
    
class Seat(models.Model):
    bus = models.ForeignKey(Bus, related_name='seats', on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)  # e.g., "1", "A1", "12B"

    class Meta:
        unique_together = ('bus', 'seat_number')

    def __str__(self):
        return f"Seat {self.seat_number} on {self.bus.number_plate}"

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, related_name='bookings', on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, related_name='bookings', on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=20)
    booked_by_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('trip', 'seat')

    def __str__(self):
        return f"Booking for {self.passenger_name} - Seat {self.seat.seat_number} on Trip {self.trip.id}"
    
    
class Payment(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50)  # e.g., "Mobile Money", "Card"
    status = models.CharField(max_length=20, default="pending")  # pending, paid, failed
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} - {self.status} - {self.amount_paid}"


class SeatBooking(models.Model):
    trip = models.ForeignKey('Trip', related_name='seat_bookings', on_delete=models.CASCADE)
    seat = models.ForeignKey('Seat', related_name='seat_bookings', on_delete=models.CASCADE)
    booking = models.ForeignKey('Booking', related_name='seat_bookings', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('trip', 'seat')

    def __str__(self):
        return f"Seat {self.seat.seat_number} on Trip {self.trip.id}"
