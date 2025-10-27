from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class AppUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # hashes the password
        user.save(using=self._db)
        return user

class AppUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AppUserManager()

    USERNAME_FIELD = "username"  # login uses username
    REQUIRED_FIELDS = ["email"]  # required when creating via createsuperuser

    def __str__(self):
        return self.username
