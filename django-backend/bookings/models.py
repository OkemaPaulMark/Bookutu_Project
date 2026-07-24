from django.db import models

from common.enums import BookingStatus
from common.ids import generate_id
from common.models import TimeStampedModel


class Booking(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    booking_reference = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='bookings')
    seat = models.ForeignKey('fleet.BusSeat', on_delete=models.CASCADE, related_name='bookings', db_column='seat_id')
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    source = models.CharField(max_length=32, default='MOBILE_APP')
    passenger_name = models.CharField(max_length=255)
    passenger_phone = models.CharField(max_length=30)
    passenger_email = models.EmailField(blank=True, null=True)
    base_fare = models.DecimalField(max_digits=12, decimal_places=2)
    seat_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    booked_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bookings')
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
