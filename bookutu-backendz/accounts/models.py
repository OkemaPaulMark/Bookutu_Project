from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting multi-tenant architecture
    """
    USER_TYPE_CHOICES = [
        ('COMPANY_STAFF', 'Company Staff'),
        ('SUPER_ADMIN', 'Super Admin'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='COMPANY_STAFF')
    
    # Multi-tenant relationship - links company staff to their company
    company = models.ForeignKey(
        'companies.Company', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='staff_members'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    

    
    def is_company_staff(self):
        return self.user_type == 'COMPANY_STAFF'
    
    def is_super_admin(self):
        return self.user_type == 'SUPER_ADMIN'
    
    def save(self, *args, **kwargs):
        # Validation: Company staff must have a company
        if self.user_type == 'COMPANY_STAFF' and not self.company:
            raise ValueError("Company staff must be assigned to a company")
        
        # Super admins should not have a company
        if self.user_type == 'SUPER_ADMIN' and self.company:
            self.company = None
            
        # Super admins should have staff privileges
        if self.user_type == 'SUPER_ADMIN':
            self.is_staff = True
            
        super().save(*args, **kwargs)


class PassengerProfile(models.Model):
    """
    Extended profile for passengers with booking-specific information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passenger_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Booking preferences
    preferred_seat_type = models.CharField(
        max_length=20,
        choices=[
            ('WINDOW', 'Window'),
            ('AISLE', 'Aisle'),
            ('ANY', 'Any')
        ],
        default='ANY'
    )
    
    # Loyalty program
    loyalty_points = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_passenger_profile'
        verbose_name = 'Passenger Profile'
        verbose_name_plural = 'Passenger Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class UserSession(models.Model):
    """
    Track user sessions for security and analytics
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('WEB', 'Web Browser'),
            ('MOBILE', 'Mobile App'),
            ('TABLET', 'Tablet'),
            ('DESKTOP', 'Desktop App')
        ],
        default='WEB'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_user_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.created_at}"


class PasswordResetToken(models.Model):
    """
    Secure password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Reset token for {self.user.email}"
