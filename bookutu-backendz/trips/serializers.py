from rest_framework import serializers
from .models import Route, Trip, TripPricing
from companies.models import Bus
from django.utils import timezone


class RouteSerializer(serializers.ModelSerializer):
    """
    Route serializer for route management
    """
    total_trips = serializers.SerializerMethodField()
    upcoming_trips = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = ('id', 'name', 'origin_city', 'origin_terminal', 'destination_city',
                 'destination_terminal', 'distance_km', 'estimated_duration_hours',
                 'base_fare', 'is_active', 'intermediate_stops', 'created_at',
                 'total_trips', 'upcoming_trips')
        read_only_fields = ('id', 'created_at', 'total_trips', 'upcoming_trips')
    
    def get_total_trips(self, obj):
        return obj.trips.count()
    
    def get_upcoming_trips(self, obj):
        return obj.trips.filter(
            departure_date__gte=timezone.now().date(),
            status='SCHEDULED'
        ).count()


class TripSerializer(serializers.ModelSerializer):
    """
    Trip serializer for trip management
    """
    route_name = serializers.CharField(source='route.name', read_only=True)
    bus_registration = serializers.CharField(source='bus.registration_number', read_only=True)
    occupancy_percentage = serializers.ReadOnlyField()
    remaining_seats = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = ('id', 'route', 'route_name', 'bus', 'bus_registration', 'departure_date',
                 'departure_time', 'arrival_time', 'base_fare', 'status', 'actual_departure_time',
                 'actual_arrival_time', 'available_seats', 'booked_seats', 'driver_name',
                 'driver_phone', 'conductor_name', 'conductor_phone', 'notes', 'created_at',
                 'occupancy_percentage', 'remaining_seats', 'is_bookable')
        read_only_fields = ('id', 'created_at', 'available_seats', 'booked_seats',
                           'occupancy_percentage', 'remaining_seats', 'is_bookable')
    
    def validate(self, attrs):
        # Ensure bus and route belong to the same company as the user
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_company_staff():
            company = request.user.company
            
            if attrs.get('bus') and attrs['bus'].company != company:
                raise serializers.ValidationError("Bus must belong to your company")
            
            if attrs.get('route') and attrs['route'].company != company:
                raise serializers.ValidationError("Route must belong to your company")
        
        return attrs


class TripPricingSerializer(serializers.ModelSerializer):
    """
    Trip pricing serializer
    """
    final_base_fare = serializers.ReadOnlyField()
    
    class Meta:
        model = TripPricing
        fields = ('peak_season_multiplier', 'demand_multiplier', 'early_bird_discount',
                 'final_base_fare', 'early_bird_days')


class TripManifestSerializer(serializers.Serializer):
    """
    Trip manifest serializer for passenger list
    """
    trip_id = serializers.IntegerField()
    trip_details = TripSerializer(read_only=True)
    passengers = serializers.ListField(child=serializers.DictField())
    total_passengers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
