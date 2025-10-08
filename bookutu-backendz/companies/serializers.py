from rest_framework import serializers
from .models import Company, Bus, BusSeat, CompanySettings
from trips.models import Route, Trip
from bookings.models import Booking
from django.utils import timezone


class CompanySerializer(serializers.ModelSerializer):
    """
    Company serializer for company profile management
    """
    total_buses = serializers.SerializerMethodField()
    total_routes = serializers.SerializerMethodField()
    total_bookings_today = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ('id', 'name', 'slug', 'description', 'email', 'phone_number', 'website',
                 'address', 'city', 'state', 'country', 'postal_code', 'registration_number',
                 'license_number', 'status', 'logo', 'cover_image', 'created_at', 'verified_at',
                 'total_buses', 'total_routes', 'total_bookings_today')
        read_only_fields = ('id', 'slug', 'status', 'created_at', 'verified_at', 
                           'total_buses', 'total_routes', 'total_bookings_today')
    
    def get_total_buses(self, obj):
        return obj.buses.filter(status='ACTIVE').count()
    
    def get_total_routes(self, obj):
        return obj.routes.filter(is_active=True).count()
    
    def get_total_bookings_today(self, obj):
        return obj.bookings.filter(created_at__date=timezone.now().date()).count()


class BusSerializer(serializers.ModelSerializer):
    """
    Bus serializer for fleet management
    """
    total_seats = serializers.SerializerMethodField()
    upcoming_trips = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = ('id', 'registration_number', 'model', 'manufacturer', 'year', 'total_seats',
                 'bus_type', 'has_ac', 'has_wifi', 'has_charging_ports', 'has_entertainment',
                 'has_restroom', 'status', 'last_maintenance', 'next_maintenance', 'image',
                 'created_at', 'upcoming_trips')
        read_only_fields = ('id', 'created_at', 'upcoming_trips')
    
    def get_total_seats(self, obj):
        return obj.seats.count()
    
    def get_upcoming_trips(self, obj):
        return obj.trips.filter(
            departure_date__gte=timezone.now().date(),
            status='SCHEDULED'
        ).count()


class BusSeatSerializer(serializers.ModelSerializer):
    """
    Bus seat serializer
    """
    class Meta:
        model = BusSeat
        fields = ('id', 'seat_number', 'row_number', 'seat_position', 'seat_type',
                 'is_window', 'is_aisle', 'has_extra_legroom', 'price_multiplier')
        read_only_fields = ('id',)


class CompanySettingsSerializer(serializers.ModelSerializer):
    """
    Company settings serializer
    """
    class Meta:
        model = CompanySettings
        fields = ('advance_booking_days', 'cancellation_hours', 'cancellation_fee_percentage',
                 'accepts_cash', 'accepts_mobile_money', 'accepts_card', 'send_sms_notifications',
                 'send_email_notifications', 'office_open_time', 'office_close_time',
                 'terms_and_conditions', 'cancellation_policy')


class CompanyDashboardStatsSerializer(serializers.Serializer):
    """
    Company dashboard statistics serializer
    """
    today_bookings = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    upcoming_trips = serializers.IntegerField()
    active_buses = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    
    # Weekly stats
    weekly_bookings = serializers.ListField(child=serializers.IntegerField())
    weekly_revenue = serializers.ListField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
