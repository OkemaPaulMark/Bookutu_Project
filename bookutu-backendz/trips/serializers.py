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
        fields = (
            "id",
            "name",
            "origin_city",
            "origin_terminal",
            "destination_city",
            "destination_terminal",
            "distance_km",
            "estimated_duration_hours",
            "base_fare",
            "is_active",
            "intermediate_stops",
            "created_at",
            "total_trips",
            "upcoming_trips",
        )
        read_only_fields = ("id", "created_at", "total_trips", "upcoming_trips")
    def get_total_trips(self, obj):
        return obj.trips.count()

    def get_upcoming_trips(self, obj):
        return obj.trips.filter(
            departure_date__gte=timezone.now().date(), status="SCHEDULED"
        ).count()


class TripSerializer(serializers.ModelSerializer):
    """
    Trip serializer for trip management
    """
    route_name = serializers.CharField(source="route.name", read_only=True)
    bus_registration = serializers.CharField(
        source="bus.registration_number", read_only=True
    )
    bus_image = serializers.ImageField(source='bus.image', required=False, allow_null=True)
    driver_full_name = serializers.CharField(
        source="driver.get_full_name", read_only=True
    )
    occupancy_percentage = serializers.ReadOnlyField()
    remaining_seats = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "route_name",
            "bus",
            "bus_registration",
            "bus_image",
            "departure_date",
            "departure_time",
            "arrival_time",
            "base_fare",
            "status",
            "actual_departure_time",
            "actual_arrival_time",
            "available_seats",
            "booked_seats",
            "driver",
            "driver_full_name",
            "conductor_name",
            "conductor_phone",
            "notes",
            "created_at",
            "occupancy_percentage",
            "remaining_seats",
            "is_bookable",
        )
        read_only_fields = (
            "id",
            "created_at",
            "available_seats",
            "booked_seats",
            "occupancy_percentage",
            "remaining_seats",
            "is_bookable",
            "driver_full_name",
        )
    def validate(self, attrs):
        # Ensure bus and route belong to the same company as the user
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_company_staff():
            company = request.user.company

            if attrs.get("bus") and attrs["bus"].company != company:
                raise serializers.ValidationError("Bus must belong to your company")

            if attrs.get("route") and attrs["route"].company != company:
                raise serializers.ValidationError("Route must belong to your company")

            if attrs.get("driver") and attrs["driver"].company != company:
                raise serializers.ValidationError("Driver must belong to your company")

        return attrs


class TripPricingSerializer(serializers.ModelSerializer):
    """
    Trip pricing serializer
    """

    final_base_fare = serializers.ReadOnlyField()

    class Meta:
        model = TripPricing
        fields = (
            "peak_season_multiplier",
            "demand_multiplier",
            "early_bird_discount",
            "final_base_fare",
            "early_bird_days",
        )

class TripManifestSerializer(serializers.Serializer):
    """
    Trip manifest serializer for passenger list
    """

    trip_id = serializers.IntegerField()
    trip_details = TripSerializer(read_only=True)
    passengers = serializers.ListField(child=serializers.DictField())
    total_passengers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class TripPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for Flutter app (GET endpoint)
    """
    route_name = serializers.CharField(source='route.name', read_only=True)
    origin = serializers.CharField(source='route.origin_city', read_only=True)
    destination = serializers.CharField(source='route.destination_city', read_only=True)
    origin_terminal = serializers.CharField(source='route.origin_terminal', read_only=True)
    destination_terminal = serializers.CharField(source='route.destination_terminal', read_only=True)
    duration_hours = serializers.DecimalField(source='route.estimated_duration_hours', max_digits=5, decimal_places=1, read_only=True)
    bus_numberplate = serializers.CharField(source='bus.license_plate', read_only=True)
    bus_type = serializers.CharField(source='bus.bus_type', read_only=True)
    capacity = serializers.IntegerField(source='bus.total_seats', read_only=True)
    amenities = serializers.SerializerMethodField()
    seats_left = serializers.SerializerMethodField()
    bus_image = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Trip
        fields = ['id', 'route_name', 'origin', 'destination', 'origin_terminal',
                  'destination_terminal', 'departure_date', 'departure_time',
                  'arrival_time', 'duration_hours', 'base_fare', 'bus_numberplate',
                  'bus_type', 'capacity', 'seats_left', 'amenities', 'bus_image',
                  'company_name', 'status']

    def get_seats_left(self, obj):
        from bookings.models import Booking
        taken = Booking.objects.filter(trip=obj, status__in=["PENDING", "CONFIRMED"]).count()
        return max(obj.bus.seats.count() - taken, 0)

    def get_amenities(self, obj):
        b = obj.bus
        return [name for name, on in [("AC", b.has_ac), ("WiFi", b.has_wifi),
                                      ("Charging", b.has_charging_ports),
                                      ("Entertainment", b.has_entertainment),
                                      ("Restroom", b.has_restroom)] if on]

    def get_bus_image(self, obj):
        request = self.context.get('request')
        if obj.bus.image and request:
            return request.build_absolute_uri(obj.bus.image.url)
        return None
