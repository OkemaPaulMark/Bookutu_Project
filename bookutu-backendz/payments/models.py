from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.managers import TenantAwareManager
import uuid

User = get_user_model()


class Payment(models.Model):
    """
    Payment records for bookings
    """
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('WALLET', 'Digital Wallet'),
    ]
    
    # Unique payment reference
    payment_reference = models.CharField(max_length=50, unique=True, editable=False)
    
    # Relationships
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # External Payment Gateway Details
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    
    # Mobile Money Details
    mobile_money_number = models.CharField(max_length=20, blank=True)
    mobile_money_provider = models.CharField(max_length=50, blank=True)  # MTN, Airtel, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    objects = TenantAwareManager()
    
    class Meta:
        db_table = 'payments_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['payment_reference']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = self.generate_payment_reference()
        
        # Ensure company consistency
        self.company = self.booking.company
        
        super().save(*args, **kwargs)
    
    def generate_payment_reference(self):
        """Generate unique payment reference"""
        prefix = "PAY"
        timestamp = timezone.now().strftime("%Y%m%d%H%M")
        random_suffix = str(uuid.uuid4())[:4].upper()
        return f"{prefix}{timestamp}{random_suffix}"
    
    def __str__(self):
        return f"{self.payment_reference} - {self.amount} {self.currency}"


class Refund(models.Model):
    """
    Refund records for cancelled bookings
    """
    REFUND_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='refunds')
    
    refund_reference = models.CharField(max_length=50, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='PENDING')
    
    # Processing details
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_refunds')
    gateway_refund_id = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments_refund'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.refund_reference:
            self.refund_reference = f"REF{timezone.now().strftime('%Y%m%d%H%M')}{str(uuid.uuid4())[:4].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.refund_reference} - {self.amount}"


class CompanyEarnings(models.Model):
    """
    Track company earnings and platform commissions
    """
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='earnings')
    
    # Date range for earnings calculation
    date = models.DateField()
    
    # Financial Summary
    total_bookings = models.PositiveIntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment breakdown
    cash_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mobile_money_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantAwareManager()
    
    class Meta:
        db_table = 'payments_company_earnings'
        verbose_name = 'Company Earnings'
        verbose_name_plural = 'Company Earnings'
        unique_together = ['company', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.company.name} - {self.date} - {self.net_earnings}"
