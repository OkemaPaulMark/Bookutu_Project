from django.db import models


class TextChoicesBase(models.TextChoices):
    @classmethod
    def values_list(cls):
        return [choice.value for choice in cls]


class UserType(TextChoicesBase):
    COMPANY_STAFF = 'COMPANY_STAFF', 'Company staff'
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super admin'
    PASSENGER = 'PASSENGER', 'Passenger'


class CompanyStatus(TextChoicesBase):
    PENDING = 'PENDING', 'Pending'
    ACTIVE = 'ACTIVE', 'Active'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    INACTIVE = 'INACTIVE', 'Inactive'


class BusStatus(TextChoicesBase):
    ACTIVE = 'ACTIVE', 'Active'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    INACTIVE = 'INACTIVE', 'Inactive'


class BookingStatus(TextChoicesBase):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'
    NO_SHOW = 'NO_SHOW', 'No show'


class PaymentStatus(TextChoicesBase):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'


class PaymentMethod(TextChoicesBase):
    CASH = 'CASH', 'Cash'
    MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile money'
    CARD = 'CARD', 'Card'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank transfer'
    WALLET = 'WALLET', 'Wallet'


class DeliveryStatus(TextChoicesBase):
    REGISTERED = 'REGISTERED', 'Registered'
    ON_DELIVERY = 'ON_DELIVERY', 'On delivery'
    PICKED_UP = 'PICKED_UP', 'Picked up'
    CANCELLED = 'CANCELLED', 'Cancelled'
