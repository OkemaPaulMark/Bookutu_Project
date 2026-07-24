from django.db import models

from common.enums import DeliveryStatus
from common.ids import generate_id
from common.models import TimeStampedModel


class Delivery(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    tracking_number = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='deliveries')

    sender_name = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=30)
    receiver_name = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=30)

    origin_terminal = models.CharField(max_length=150)
    destination_terminal = models.CharField(max_length=150)
    package_description = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.REGISTERED)
    registered_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='registered_deliveries',
    )
    picked_up_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_deliveries',
    )
    picked_up_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'deliveries'
        ordering = ['-created_at']
