from rest_framework import serializers

from companies.models import Company

from .models import Bus, BusSeat, Driver, Route


class BusSeatSerializer(serializers.ModelSerializer):
    bus_id = serializers.CharField(read_only=True)

    class Meta:
        model = BusSeat
        fields = [
            'id', 'bus_id', 'seat_number', 'row_number', 'seat_position',
            'seat_type', 'is_window', 'is_aisle', 'has_extra_legroom', 'price_multiplier',
        ]


class BusSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)
    seats = BusSeatSerializer(many=True, read_only=True)
    _count = serializers.SerializerMethodField(method_name='get_counts')

    class Meta:
        model = Bus
        fields = [
            'id', 'company_id', 'license_plate', 'model', 'make', 'year', 'total_seats',
            'bus_type', 'has_entertainment', 'has_restroom', 'status', 'image_url',
            'created_at', 'updated_at', 'seats', '_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_counts(self, obj):
        return {'seats': obj.seats.count(), 'trips': obj.trips.count()}


class RouteSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)

    class Meta:
        model = Route
        fields = [
            'id', 'company_id', 'name', 'origin_city', 'origin_terminal',
            'destination_city', 'destination_terminal', 'distance_km',
            'estimated_duration_hours', 'base_fare', 'is_active',
            'intermediate_stops', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)

    class Meta:
        model = Driver
        fields = [
            'id', 'company_id', 'first_name', 'last_name', 'phone_number', 'email',
            'license_number', 'license_expiry_date', 'date_of_birth', 'employee_id',
            'hire_date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
