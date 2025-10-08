from django.contrib import admin
from .models import Company, Bus, BusSeat, Driver, CompanySettings

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'email', 'phone_number', 'city', 'country', 'commission_rate')
    list_filter = ('status', 'country')
    search_fields = ('name', 'email', 'phone_number', 'city')
    ordering = ('name',)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'company', 'model', 'make', 'year', 'bus_type', 'status')
    list_filter = ('bus_type', 'status', 'company')
    search_fields = ('license_plate', 'model', 'make')
    ordering = ('license_plate',)

@admin.register(BusSeat)
class BusSeatAdmin(admin.ModelAdmin):
    list_display = ('bus', 'seat_number', 'row_number', 'seat_position', 'seat_type', 'is_window', 'is_aisle')
    list_filter = ('seat_type',)
    search_fields = ('bus__license_plate', 'seat_number')
    ordering = ('bus', 'row_number', 'seat_position')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'license_number', 'status', 'phone_number', 'email')
    list_filter = ('status', 'company')
    search_fields = ('first_name', 'last_name', 'license_number', 'phone_number', 'email')
    ordering = ('last_name', 'first_name')

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('company', 'advance_booking_days', 'cancellation_hours', 'cancellation_fee_percentage')
    search_fields = ('company__name',)
    ordering = ('company',)
