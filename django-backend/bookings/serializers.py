from rest_framework import serializers

from authentication.models import User
from companies.models import Company
from fleet.models import BusSeat
from trips.models import Trip

from .models import Booking


class _RouteSummarySerializer(serializers.Serializer):
    origin_city = serializers.CharField()
    destination_city = serializers.CharField()


class _BusSummarySerializer(serializers.Serializer):
    license_plate = serializers.CharField()


class _CompanySummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class _TripSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    departure_date = serializers.DateTimeField()
    departure_time = serializers.CharField()
    arrival_time = serializers.CharField()
    company = _CompanySummarySerializer()
    route = _RouteSummarySerializer()
    bus = _BusSummarySerializer()


class _SeatSummarySerializer(serializers.Serializer):
    seat_number = serializers.CharField()


class _PassengerSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class _PaymentSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)


class BookingSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)
    trip_id = serializers.PrimaryKeyRelatedField(source='trip', queryset=Trip.objects.all())
    trip = _TripSummarySerializer(read_only=True)
    passenger_id = serializers.PrimaryKeyRelatedField(source='passenger', queryset=User.objects.all(), required=False)
    passenger = _PassengerSummarySerializer(read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(source='seat', queryset=BusSeat.objects.all())
    seat = _SeatSummarySerializer(read_only=True)
    passenger_name = serializers.CharField(required=False, allow_blank=True)
    passenger_phone = serializers.CharField(required=False, allow_blank=True)
    payments = _PaymentSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'company_id', 'trip_id', 'trip',
            'passenger_id', 'passenger', 'seat_id', 'seat',
            'status', 'source', 'passenger_name', 'passenger_phone', 'passenger_email',
            'base_fare', 'seat_fee', 'service_fee', 'total_amount',
            'created_at', 'confirmed_at', 'cancelled_at', 'payments',
        ]
        read_only_fields = [
            'id', 'booking_reference', 'base_fare', 'seat_fee', 'service_fee', 'total_amount',
            'created_at', 'confirmed_at', 'cancelled_at',
        ]
