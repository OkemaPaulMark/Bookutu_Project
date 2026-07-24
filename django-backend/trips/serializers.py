from rest_framework import serializers

from companies.models import Company
from fleet.models import Bus, Driver, Route
from fleet.serializers import BusSerializer, DriverSerializer, RouteSerializer

from .models import Trip, TripPricing


class _CompanySummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class TripSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)
    company = _CompanySummarySerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(source='route', queryset=Route.objects.all())
    route = RouteSerializer(read_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(source='bus', queryset=Bus.objects.all())
    bus = BusSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(source='driver', queryset=Driver.objects.all(), required=False, allow_null=True)
    driver = DriverSerializer(read_only=True)
    _count = serializers.SerializerMethodField(method_name='get_counts')

    class Meta:
        model = Trip
        fields = [
            'id', 'company_id', 'company', 'route_id', 'route', 'bus_id', 'bus', 'driver_id', 'driver',
            'departure_date', 'departure_time', 'arrival_time', 'base_fare', 'status',
            'available_seats', 'booked_seats', 'notes', 'created_at', 'updated_at', '_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'available_seats', 'booked_seats']

    def get_counts(self, obj):
        return {'bookings': obj.bookings.count()}


class TripPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPricing
        fields = '__all__'
