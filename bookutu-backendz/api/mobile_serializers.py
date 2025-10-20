from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from bookings.models import Booking, SeatReservation
from companies.models import BusSeat, Company
from trips.models import Trip
from accounts.models import PassengerProfile


User = get_user_model()


class MobileUserSerializer(serializers.ModelSerializer):
    passenger_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "passenger_profile",
        ]

    def get_passenger_profile(self, obj):
        try:
            profile = obj.passenger_profile
            return {
                "date_of_birth": profile.date_of_birth,
                "emergency_contact": profile.emergency_contact,
                "emergency_phone": profile.emergency_phone,
                "preferred_payment_method": getattr(
                    profile, "preferred_payment_method", None
                ),
            }
        except PassengerProfile.DoesNotExist:
            return None


class MobileCompanySerializer(serializers.ModelSerializer):
    """Lightweight company info for mobile"""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ["id", "name", "logo_url", "phone_number"]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None


class MobileTripSearchSerializer(serializers.Serializer):
    """Trip search parameters for mobile"""

    origin = serializers.CharField(max_length=100)
    destination = serializers.CharField(max_length=100)
    departure_date = serializers.DateField()
    passengers = serializers.IntegerField(min_value=1, max_value=10, default=1)
    bus_type = serializers.ChoiceField(
        choices=[("STANDARD", "Standard"), ("LUXURY", "Luxury"), ("VIP", "VIP")],
        required=False,
    )


class MobileTripSerializer(serializers.ModelSerializer):
    """Optimized trip info for mobile listing"""

    company = MobileCompanySerializer(read_only=True)
    route_info = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "company",
            "route_info",
            "departure_time",
            "arrival_time",
            "available_seats",
            "duration",
        ]

    def get_route_info(self, obj):
        return {
            "origin": obj.route.origin_city,
            "destination": obj.route.destination_city,
            "distance_km": obj.route.distance_km,
        }

    def get_available_seats(self, obj):
        # Compute based on actual bookings to include PENDING holds
        booked = Booking.objects.filter(
            trip=obj, status__in=["PENDING", "CONFIRMED"]
        ).count()
        return max(obj.bus.total_seats - booked, 0)

    def get_duration(self, obj):
        # Display as string based on route estimated_duration_hours
        return f"{obj.route.estimated_duration_hours}h"


class MobileSeatSerializer(serializers.ModelSerializer):
    """Seat info for mobile seat selection"""

    price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = BusSeat
        fields = [
            "id",
            "seat_number",
            "row_number",
            "seat_position",
            "seat_type",
            "price",
            "is_available",
        ]

    def get_price(self, obj):
        trip = self.context.get("trip")
        if trip and hasattr(trip, "pricing"):
            return float(
                trip.pricing.calculate_final_fare(
                    seat_type_multiplier=obj.price_multiplier
                )
            )
        # Fallback to trip.base_fare with seat multiplier if pricing not set
        if trip:
            return float(trip.base_fare * obj.price_multiplier)
        return None

    def get_is_available(self, obj):
        trip = self.context.get("trip")
        if not trip:
            return True
        # Seat is available if not already booked for this trip (including PENDING and CONFIRMED)
        return not Booking.objects.filter(
            trip=trip, seat=obj, status__in=["PENDING", "CONFIRMED"]
        ).exists()


class MobileBookingCreateSerializer(serializers.Serializer):
    """Create a single-seat booking from mobile app"""

    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    seat = serializers.PrimaryKeyRelatedField(
        queryset=BusSeat.objects.all(), required=False, allow_null=True
    )
    seat_number = serializers.CharField(required=False, allow_blank=True)
    passenger_name = serializers.CharField(required=False, allow_blank=True)
    passenger_phone = serializers.CharField(required=False, allow_blank=True)
    passenger_email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        trip = attrs["trip"]
        seat = attrs.get("seat")
        seat_number = attrs.get("seat_number")

        # Ensure trip is bookable
        if not trip.is_bookable():
            raise serializers.ValidationError("Trip is not available for booking")

        # Resolve seat by seat_number if provided
        if not seat and seat_number:
            try:
                seat = BusSeat.objects.get(bus=trip.bus, seat_number=seat_number)
                attrs["seat"] = seat
            except BusSeat.DoesNotExist:
                raise serializers.ValidationError(
                    "Seat number does not exist on this bus"
                )

        if not seat:
            raise serializers.ValidationError(
                "Seat is required (provide seat id or seat_number)"
            )

        # Seat must belong to trip bus
        if seat.bus != trip.bus:
            raise serializers.ValidationError(
                "Selected seat does not belong to the trip bus"
            )

        # Check availability
        if Booking.objects.filter(
            trip=trip, seat=seat, status__in=["PENDING", "CONFIRMED"]
        ).exists():
            raise serializers.ValidationError("Seat is already booked")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        trip: Trip = validated_data["trip"]
        seat: BusSeat = validated_data["seat"]

        # Attempt to reserve the seat to avoid race conditions
        try:
            SeatReservation.objects.create(trip=trip, seat=seat, user=user)
        except IntegrityError:
            # Another active reservation exists
            raise serializers.ValidationError(
                "Seat is currently reserved. Please try another seat or try again shortly."
            )

        # Compute pricing
        if hasattr(trip, "pricing"):
            total_amount = trip.pricing.calculate_final_fare(
                seat_type_multiplier=seat.price_multiplier
            )
            base_fare = trip.base_fare
            seat_fee = total_amount - base_fare
        else:
            total_amount = trip.base_fare * seat.price_multiplier
            base_fare = trip.base_fare
            seat_fee = total_amount - base_fare
        service_fee = 0

        # Passenger info fallback from user
        passenger_name = (
            validated_data.get("passenger_name")
            or f"{user.first_name} {user.last_name}".strip()
        )
        passenger_phone = validated_data.get("passenger_phone") or getattr(
            user, "phone_number", ""
        )
        passenger_email = validated_data.get("passenger_email") or user.email

        booking = Booking.objects.create(
            company=trip.company,
            trip=trip,
            passenger=user,
            seat=seat,
            status="PENDING",
            source="MOBILE_APP",
            passenger_name=passenger_name,
            passenger_phone=passenger_phone,
            passenger_email=passenger_email or "",
            base_fare=base_fare,
            seat_fee=seat_fee,
            service_fee=service_fee,
            total_amount=total_amount,
        )

        return booking


class MobileBookingSerializer(serializers.ModelSerializer):
    """Booking details for mobile"""

    trip_info = serializers.SerializerMethodField()
    seat_info = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "booking_reference",
            "status",
            "trip_info",
            "seat_info",
            "total_amount",
            "payment_info",
            "created_at",
            "qr_code",
        ]

    def get_trip_info(self, obj):
        return {
            "company_name": obj.trip.company.name,
            "route": f"{obj.trip.route.origin_city} → {obj.trip.route.destination_city}",
            "departure_time": obj.trip.departure_time,
            "arrival_time": obj.trip.arrival_time,
            "departure_date": obj.trip.departure_date,
            "bus_type": obj.trip.bus.bus_type,
        }

    def get_seat_info(self, obj):
        if obj.seat:
            # Compute displayed price similar to creation
            if hasattr(obj.trip, "pricing"):
                price = float(
                    obj.trip.pricing.calculate_final_fare(
                        seat_type_multiplier=obj.seat.price_multiplier
                    )
                )
            else:
                price = float(obj.trip.base_fare * obj.seat.price_multiplier)
            return {
                "seat_number": obj.seat.seat_number,
                "seat_type": obj.seat.seat_type,
                "price": price,
            }
        return None

    def get_payment_info(self, obj):
        payment = obj.payments.first()
        if payment:
            return {
                "status": payment.status,
                "method": payment.payment_method,
                "transaction_id": payment.gateway_transaction_id,
            }
        return None

    def get_qr_code(self, obj):
        return f"BOOKUTU:{obj.booking_reference}:{obj.id}"


class MobileNotificationSerializer(serializers.Serializer):
    """Push notification registration"""

    device_token = serializers.CharField(max_length=255)
    device_type = serializers.ChoiceField(
        choices=[("ios", "iOS"), ("android", "Android")]
    )
    app_version = serializers.CharField(max_length=20, required=False)
