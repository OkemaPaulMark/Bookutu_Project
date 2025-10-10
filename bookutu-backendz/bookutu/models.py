from django.db import models
from django.utils import timezone


class SystemSettings(models.Model):
    """
    Global system settings for the Bookutu platform
    """
    # Platform Information
    platform_name = models.CharField(max_length=100, default='Bookutu')
    platform_tagline = models.CharField(max_length=200, default='Your Trusted Bus Booking Platform')
    platform_description = models.TextField(default='Book bus tickets easily and securely across Uganda')
    
    # Contact Information
    support_email = models.EmailField(default='support@bookutu.com')
    support_phone = models.CharField(max_length=20, default='+256700000000')
    
    # Business Settings
    default_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    currency = models.CharField(max_length=3, default='UGX')
    
    # Platform Features
    allow_company_registration = models.BooleanField(default=True)
    require_company_verification = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    # Notification Settings
    send_booking_confirmations = models.BooleanField(default=True)
    send_payment_notifications = models.BooleanField(default=True)
    
    # Terms and Policies
    terms_of_service = models.TextField(blank=True)
    privacy_policy = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookutu_system_settings'
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"{self.platform_name} Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Advert(models.Model):
    """Platform-wide adverts managed by super admins"""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="adverts/")
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookutu_adverts"
        ordering = ["-created_at"]
        verbose_name = "Advert"
        verbose_name_plural = "Adverts"

    def __str__(self) -> str:
        return self.title

    @property
    def is_within_schedule(self) -> bool:
        today = timezone.now().date()
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True
