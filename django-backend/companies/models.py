from django.db import models

from common.enums import CompanyStatus
from common.ids import generate_id
from common.models import TimeStampedModel


class Company(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default='Uganda')
    postal_code = models.CharField(max_length=30, blank=True, null=True)
    registration_number = models.CharField(max_length=120, unique=True)
    tax_id = models.CharField(max_length=120, blank=True, null=True)
    license_number = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=CompanyStatus.choices, default=CompanyStatus.PENDING)
    commission_rate = models.DecimalField(max_digits=6, decimal_places=2, default=10.00)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'companies'
        ordering = ['-created_at']


class CompanyEarnings(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='earnings')
    date = models.DateTimeField()
    total_bookings = models.IntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mobile_money_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'company_earnings'
        unique_together = ('company', 'date')
