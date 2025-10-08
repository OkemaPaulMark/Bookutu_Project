from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'SUPER_ADMIN')
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def create_company_staff(self, email, company, password=None, **extra_fields):
        """
        Create a company staff member
        """
        extra_fields.setdefault('user_type', 'COMPANY_STAFF')
        extra_fields['company'] = company
        return self.create_user(email, password, **extra_fields)
    
    def create_passenger(self, email, password=None, **extra_fields):
        """
        Create a passenger user
        """
        extra_fields.setdefault('user_type', 'PASSENGER')
        return self.create_user(email, password, **extra_fields)


class TenantAwareManager(models.Manager):
    """
    Manager that automatically filters queries by company for multi-tenant data isolation
    """
    
    def __init__(self, tenant_field='company'):
        super().__init__()
        self.tenant_field = tenant_field
    
    def get_queryset(self):
        # This will be enhanced by middleware to automatically filter by tenant
        return super().get_queryset()
    
    def for_company(self, company):
        """
        Explicitly filter by company
        """
        filter_kwargs = {self.tenant_field: company}
        return self.get_queryset().filter(**filter_kwargs)
