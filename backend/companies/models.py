from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.managers import TenantAwareManager


class Company(models.Model):
    """
    Bus company model for multi-tenant architecture
    """

    COMPANY_STATUS_CHOICES = [
        ("PENDING", "Pending Verification"),
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("INACTIVE", "Inactive"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True)

    # Address Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Uganda")
    postal_code = models.CharField(max_length=20, blank=True)

    # Business Information
    registration_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=100)

    # Platform Settings
    status = models.CharField(
        max_length=20, choices=COMPANY_STATUS_CHOICES, default="PENDING"
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00
    )  # Platform commission %

    # Media
    logo = models.ImageField(upload_to="companies/logos/", blank=True)
    cover_image = models.ImageField(upload_to="companies/covers/", blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "companies_company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_active(self):
        return self.status == "ACTIVE"

    def verify(self):
        """Mark company as verified and active"""
        self.status = "ACTIVE"
        self.verified_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        # Auto-generate unique slug from name if not provided
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            candidate = base_slug or "company"
            suffix = 1
            while Company.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                suffix += 1
                candidate = f"{base_slug}-{suffix}"
            self.slug = candidate
        super().save(*args, **kwargs)


class Bus(models.Model):
    """
    Bus/Vehicle model for fleet management
    """

    BUS_TYPE_CHOICES = [
        ("STANDARD", "Standard"),
        ("LUXURY", "Luxury"),
        ("VIP", "VIP"),
        ("SLEEPER", "Sleeper"),
    ]

    BUS_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("MAINTENANCE", "Under Maintenance"),
        ("INACTIVE", "Inactive"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="buses")

    # Bus Details
    license_plate = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    # Capacity and Layout
    total_seats = models.PositiveIntegerField()
    bus_type = models.CharField(
        max_length=20, choices=BUS_TYPE_CHOICES, default="STANDARD"
    )

    # Features
    has_ac = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    has_charging_ports = models.BooleanField(default=False)
    has_entertainment = models.BooleanField(default=False)
    has_restroom = models.BooleanField(default=False)

    # Status and Maintenance
    status = models.CharField(
        max_length=20, choices=BUS_STATUS_CHOICES, default="ACTIVE"
    )
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)

    # Media
    image = models.ImageField(upload_to="buses/", blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        db_table = "companies_bus"
        verbose_name = "Bus"
        verbose_name_plural = "Buses"
        ordering = ["license_plate"]

    def __str__(self):
        return f"{self.company.name} - {self.license_plate}"

    def is_available(self):
        return self.status == "ACTIVE"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Automatically create seatmap if new bus and no seats exist
        if is_new and self.total_seats > 0 and not self.seats.exists():
            seats_per_row = 4
            num_rows = self.total_seats // seats_per_row
            seat_positions = [
                "LEFT_WINDOW",
                "LEFT_AISLE",
                "RIGHT_AISLE",
                "RIGHT_WINDOW",
            ]
            seat_letters = ["A", "B", "C", "D"]
            for row in range(1, num_rows + 1):
                for i in range(seats_per_row):
                    seat_number = f"{row}{seat_letters[i]}"
                    BusSeat.objects.create(
                        bus=self,
                        seat_number=seat_number,
                        row_number=row,
                        seat_position=seat_positions[i],
                        seat_type="REGULAR",
                        is_window=(i == 0 or i == 3),
                        is_aisle=(i == 1 or i == 2),
                        has_extra_legroom=False,
                        price_multiplier=1.00,
                    )


class BusSeat(models.Model):
    """
    Individual seat configuration for each bus
    """

    SEAT_TYPE_CHOICES = [
        ("REGULAR", "Regular"),
        ("PREMIUM", "Premium"),
        ("VIP", "VIP"),
    ]

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)  # e.g., "1A", "12B"
    row_number = models.PositiveIntegerField()
    seat_position = models.CharField(max_length=10)  # 'LEFT', 'CENTER', 'RIGHT'
    seat_type = models.CharField(
        max_length=20, choices=SEAT_TYPE_CHOICES, default="REGULAR"
    )

    # Seat features
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    has_extra_legroom = models.BooleanField(default=False)

    # Pricing
    price_multiplier = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.00
    )  # 1.0 = base price, 1.5 = 50% more

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies_bus_seat"
        verbose_name = "Bus Seat"
        verbose_name_plural = "Bus Seats"
        unique_together = ["bus", "seat_number"]
        ordering = ["row_number", "seat_position"]

    def __str__(self):
        return f"{self.bus.license_plate} - Seat {self.seat_number}"


class Driver(models.Model):
    """
    Driver information for company fleet
    """

    DRIVER_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("SUSPENDED", "Suspended"),
        ("ON_LEAVE", "On Leave"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="drivers"
    )

    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Driver Details
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry_date = models.DateField()
    date_of_birth = models.DateField()

    # Employment Details
    employee_id = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=DRIVER_STATUS_CHOICES, default="ACTIVE"
    )

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    # Performance Metrics
    total_trips = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        db_table = "companies_driver"
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_license_valid(self):
        from django.utils import timezone

        return self.license_expiry_date > timezone.now().date()


class CompanySettings(models.Model):
    """
    Company-specific settings and preferences
    """

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="settings"
    )

    # Booking Settings
    advance_booking_days = models.PositiveIntegerField(
        default=30
    )  # How many days in advance can customers book
    cancellation_hours = models.PositiveIntegerField(
        default=24
    )  # Hours before departure for free cancellation
    cancellation_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00
    )

    # Payment Settings
    accepts_cash = models.BooleanField(default=True)
    accepts_mobile_money = models.BooleanField(default=True)
    accepts_card = models.BooleanField(default=False)

    # Notification Settings
    send_sms_notifications = models.BooleanField(default=True)
    send_email_notifications = models.BooleanField(default=True)

    # Business Hours
    office_open_time = models.TimeField(default="08:00")
    office_close_time = models.TimeField(default="18:00")

    # Terms and Conditions
    terms_and_conditions = models.TextField(blank=True)
    cancellation_policy = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies_settings"
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return f"Settings for {self.company.name}"
