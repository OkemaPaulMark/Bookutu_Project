from django.db import models

from common.enums import PaymentMethod, PaymentStatus
from common.ids import generate_id
from common.models import TimeStampedModel


class Payment(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    payment_reference = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='UGX')
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    gateway_transaction_id = models.CharField(max_length=120, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    mobile_money_number = models.CharField(max_length=50, blank=True, null=True)
    mobile_money_provider = models.CharField(max_length=80, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']


class Refund(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    refund_reference = models.CharField(max_length=50, unique=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=30, default='PENDING')
    processed_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    gateway_refund_id = models.CharField(max_length=120, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'refunds'
