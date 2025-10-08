from django.contrib import admin
from .models import Booking, BookingCancellation, BookingHistory, SeatReservation

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'passenger_name', 'trip', 'company', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'source', 'company', 'created_at')
    search_fields = ('booking_reference', 'passenger_name', 'passenger_phone', 'passenger_email')
    ordering = ('-created_at',)

@admin.register(BookingCancellation)
class BookingCancellationAdmin(admin.ModelAdmin):
    list_display = ('booking', 'reason', 'cancelled_by', 'cancellation_fee', 'refund_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('booking__booking_reference', 'reason')
    ordering = ('-created_at',)

@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'action', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('booking__booking_reference', 'description')
    ordering = ('-created_at',)

@admin.register(SeatReservation)
class SeatReservationAdmin(admin.ModelAdmin):
    list_display = ('trip', 'seat', 'user', 'expires_at', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('trip__route__name', 'user__email')
    ordering = ('-created_at',)
