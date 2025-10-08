from rest_framework import serializers
from django.contrib.auth import get_user_model
from bookings.models import Booking
from companies.models import BusSeat

from trips.models import Trip
from bookings.models import Booking
from companies.models import Company
from accounts.models import PassengerProfile



User = get_user_model()
class MobileUserSerializer(serializers.ModelSerializer):
    passenger_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 'user_type',
            'passenger_profile'
        ]

    def get_passenger_profile(self, obj):
        try:
            profile = obj.passenger_profile
            return {
                'date_of_birth': profile.date_of_birth,
                'emergency_contact': profile.emergency_contact,
                'emergency_phone': profile.emergency_phone,
                'preferred_payment_method': getattr(profile, 'preferred_payment_method', None),
            }
        except PassengerProfile.DoesNotExist:
            return None


class MobileSeatSerializer(serializers.ModelSerializer):
    """Seat info for mobile seat selection"""
    price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = BusSeat
        fields = ['id', 'seat_number', 'row_number', 'seat_position', 'seat_type', 'price', 'is_available']

    def get_price(self, obj):
        # Calculate price using trip pricing if available
        trip = self.context.get('trip')
        if trip and hasattr(trip, 'pricing'):
            return trip.pricing.calculate_final_fare(seat_type_multiplier=obj.price_multiplier)
        return None

    def get_is_available(self, obj):
        trip = self.context.get('trip')
        if not trip:
            return True
        # Seat is available if not already booked for this trip
        return not Booking.objects.filter(trip=trip, seat=obj, status='CONFIRMED').exists()


class MobileCompanySerializer(serializers.ModelSerializer):
    """Lightweight company info for mobile"""
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'logo_url', 'rating', 'phone_number']

    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None


class MobileTripSearchSerializer(serializers.Serializer):
    """Trip search parameters for mobile"""
    origin = serializers.CharField(max_length=100)
    destination = serializers.CharField(max_length=100)
    departure_date = serializers.DateField()
    passengers = serializers.IntegerField(min_value=1, max_value=10, default=1)
    bus_type = serializers.ChoiceField(
        choices=[('standard', 'Standard'), ('luxury', 'Luxury'), ('vip', 'VIP')],
        required=False
    )


class MobileTripSerializer(serializers.ModelSerializer):
    """Optimized trip info for mobile listing"""
    company = MobileCompanySerializer(read_only=True)
    route_info = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'company', 'route_info', 'departure_time',
            'arrival_time', 'available_seats', 'price_range',
            'duration', 'bus_type', 'amenities'
        ]

    def get_route_info(self, obj):
        return {
            'origin': obj.route.origin,
            'destination': obj.route.destination,
            'distance': obj.route.distance_km
        }

    def get_available_seats(self, obj):
        return obj.get_available_seats_count()

    def get_price_range(self, obj):
        prices = obj.bus.seats.values_list('price', flat=True).distinct()
        if prices:
            return {'min': min(prices), 'max': max(prices)}
        return {'min': 0, 'max': 0}

    def get_duration(self, obj):
        if obj.departure_time and obj.arrival_time:
            duration = obj.arrival_time - obj.departure_time
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return None


class MobileSeatSerializer(serializers.ModelSerializer):
    """Seat info for mobile seat selection"""
    class Meta:
        model = BusSeat
        fields = ['id', 'seat_number', 'seat_type', 'price', 'is_available', 'position']


class MobileBookingCreateSerializer(serializers.ModelSerializer):
    """Create booking from mobile app"""
    passenger_details = serializers.JSONField()
    selected_seats = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=10
    )

    class Meta:
        model = Booking
        fields = [
            'trip', 'passenger_details', 'selected_seats',
            'payment_method', 'special_requests'
        ]

    def validate_selected_seats(self, value):
        """Validate seat availability"""
        trip_id = self.initial_data.get('trip')
        if trip_id:
            unavailable_seats = BusSeat.objects.filter(
                bus__trips__id=trip_id,
                id__in=value,
                is_available=False
            ).values_list('id', flat=True)

            if unavailable_seats:
                raise serializers.ValidationError(
                    f"Seats {list(unavailable_seats)} are not available"
                )
        return value

def create(self, validated_data):
    selected_seats = validated_data.pop('selected_seats')
    passenger_details = validated_data.pop('passenger_details')
    user = self.context['request'].user
    trip = validated_data['trip']

    bookings = []
    for seat_id in selected_seats:
        seat = BusSeat.objects.get(id=seat_id)

        booking = Booking.objects.create(
            passenger=user,
            passenger_name=passenger_details.get('name'),
            passenger_phone=passenger_details.get('phone'),
            passenger_email=passenger_details.get('email'),
            seat=seat,
            **validated_data
        )
        bookings.append(booking)

    # If multiple seats booked, return first one (or extend logic later)
    return bookings[0]



class MobileBookingSerializer(serializers.ModelSerializer):
    """Booking details for mobile"""
    trip_info = serializers.SerializerMethodField()
    seat_info = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'status', 'trip_info',
            'seat_info', 'total_amount', 'payment_info',
            'created_at', 'qr_code', 'special_requests'
        ]

    def get_trip_info(self, obj):
        return {
            'company_name': obj.trip.company.name,
            'route': f"{obj.trip.route.origin} → {obj.trip.route.destination}",
            'departure_time': obj.trip.departure_time,
            'arrival_time': obj.trip.arrival_time,
            'departure_date': obj.trip.departure_date,
            'bus_type': obj.trip.bus_type
        }

    def get_seat_info(self, obj):
        if obj.seat:
            return {
                'seat_number': obj.seat.seat_number,
                'seat_type': obj.seat.seat_type,
                'price': obj.seat.price
            }
        return None

    def get_payment_info(self, obj):
        payment = obj.payments.first()
        if payment:
            return {
                'status': payment.status,
                'method': payment.payment_method,
                'transaction_id': payment.transaction_id
            }
        return None

    def get_qr_code(self, obj):
        return f"BOOKUTU:{obj.booking_reference}:{obj.id}"


class MobileNotificationSerializer(serializers.Serializer):
    """Push notification registration"""
    device_token = serializers.CharField(max_length=255)
    device_type = serializers.ChoiceField(choices=[('ios', 'iOS'), ('android', 'Android')])
    app_version = serializers.CharField(max_length=20, required=False)
