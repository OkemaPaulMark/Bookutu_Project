from rest_framework import serializers
from django.contrib.auth import get_user_model
from companies.models import Company
from bookings.models import Booking
from payments.models import Payment

User = get_user_model()


class SuperAdminCompanySerializer(serializers.ModelSerializer):
    """
    Super admin company serializer with extended information
    """
    total_buses = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ('id', 'name', 'email', 'phone_number', 'city', 'status',
                 'registration_number', 'commission_rate', 'created_at', 'verified_at',
                 'total_buses', 'total_bookings', 'total_revenue', 'staff_count')
    
    def get_total_buses(self, obj):
        return obj.buses.count()
    
    def get_total_bookings(self, obj):
        return obj.bookings.count()
    
    def get_total_revenue(self, obj):
        return float(obj.payments.filter(status='COMPLETED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0)
    
    def get_staff_count(self, obj):
        return obj.staff_members.count()


class SuperAdminUserSerializer(serializers.ModelSerializer):
    """
    Super admin user serializer with extended information
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    total_bookings = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number',
                 'user_type', 'company_name', 'is_verified', 'is_active',
                 'date_joined', 'last_login', 'total_bookings')
    
    def get_total_bookings(self, obj):
        if obj.user_type == 'PASSENGER':
            return obj.bookings.count()
        return 0


class PlatformStatsSerializer(serializers.Serializer):
    """
    Platform statistics serializer
    """
    total_companies = serializers.IntegerField()
    active_companies = serializers.IntegerField()
    pending_companies = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    today_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    weekly_trends = serializers.DictField()


class AnnouncementSerializer(serializers.Serializer):
    """
    Platform announcement serializer
    """
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    target_audience = serializers.ChoiceField(
        choices=[('all', 'All Users'), ('companies', 'Companies'), ('passengers', 'Passengers')],
        default='all'
    )
    priority = serializers.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
