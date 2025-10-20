from rest_framework import serializers
from .models import Booking, BookingCancellation, BookingHistory, SeatReservation
from companies.models import BusSeat
from trips.models import Trip
from django.contrib.auth import get_user_model
from django.utils import timezone
from payments.models import Payment

User = get_user_model()


class BookingSerializer(serializers.ModelSerializer):
    """
    Booking serializer for booking management
    """

    trip_details = serializers.SerializerMethodField()
    seat_details = serializers.SerializerMethodField()
    passenger_details = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    cancellation_fee = serializers.SerializerMethodField()
    # expose seat number explicitly for convenience in some UIs
    seat_number = serializers.CharField(source="seat.seat_number", read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "booking_reference",
            "trip",
            "passenger",
            "seat",
            "status",
            "source",
            "passenger_name",
            "passenger_phone",
            "passenger_email",
            "base_fare",
            "seat_fee",
            "service_fee",
            "total_amount",
            "created_at",
            "confirmed_at",
            "cancelled_at",
            "trip_details",
            "seat_details",
            "passenger_details",
            "can_cancel",
            "cancellation_fee",
            "seat_number",
        )  # Added seat_number for direct booking form
        read_only_fields = (
            "id",
            "booking_reference",
            "created_at",
            "confirmed_at",
            "cancelled_at",
            "trip_details",
            "seat_details",
            "passenger_details",
            "can_cancel",
            "cancellation_fee",
        )

    def get_trip_details(self, obj):
        return {
            "route_name": f"{obj.trip.route.origin_city} → {obj.trip.route.destination_city}",
            "departure_date": obj.trip.departure_date,
            "departure_time": obj.trip.departure_time,
            "bus_registration": obj.trip.bus.license_plate,
            "available_seats": obj.trip.remaining_seats,  # Added available seats
        }

    def get_seat_details(self, obj):
        return {
            "seat_number": obj.seat.seat_number,
            "seat_type": obj.seat.seat_type,
            "is_window": obj.seat.is_window,
        }

    def get_passenger_details(self, obj):
        return {
            "name": obj.passenger_name,
            "phone": obj.passenger_phone,
            "email": obj.passenger_email,
        }

    def get_can_cancel(self, obj):
        if obj.status != "CONFIRMED":
            return False

        # Check if within cancellation window
        company_settings = obj.company.settings
        # Ensure both datetimes are timezone-aware
        departure_dt = timezone.make_aware(
            timezone.datetime.combine(obj.trip.departure_date, obj.trip.departure_time)
        )
        now = timezone.now()
        hours_until_departure = (departure_dt - now).total_seconds() / 3600

        return hours_until_departure >= company_settings.cancellation_hours

    def get_cancellation_fee(self, obj):
        return float(obj.calculate_cancellation_fee())


class DirectBookingSerializer(serializers.ModelSerializer):
    """
    Direct booking serializer for company staff
    """

    seat_number = serializers.CharField(
        write_only=True, required=False
    )  # For selecting a seat by number
    payment_method = serializers.ChoiceField(
        choices=[choice[0] for choice in Payment.PAYMENT_METHOD_CHOICES],
        write_only=True,
        required=True,
    )
    mobile_money_number = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    mobile_money_provider = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Booking
        fields = (
            "trip",
            "seat",
            "seat_number",
            "passenger_name",
            "passenger_phone",
            "passenger_email",
            "payment_method",
            "mobile_money_number",
            "mobile_money_provider",
        )
        extra_kwargs = {
            "seat": {
                "required": False
            }  # Make seat optional as we might use seat_number
        }

    def validate(self, attrs):
        trip = attrs["trip"]
        seat = attrs.get("seat")
        seat_number = attrs.get("seat_number")

        if not seat and not seat_number:
            raise serializers.ValidationError(
                "Either 'seat' or 'seat_number' must be provided."
            )

        if seat_number:
            # Find the seat by number for the trip's bus
            try:
                seat = BusSeat.objects.get(bus=trip.bus, seat_number=seat_number)
                attrs["seat"] = seat  # Assign the found seat to attrs
            except BusSeat.DoesNotExist:
                raise serializers.ValidationError(
                    f"Seat number {seat_number} does not exist for this trip's bus."
                )

        # Validate seat belongs to the trip's bus
        if seat.bus != trip.bus:
            raise serializers.ValidationError(
                "Seat does not belong to the selected trip's bus"
            )

        # Check if seat is available
        existing_booking = Booking.objects.filter(
            trip=trip, seat=seat, status__in=["PENDING", "CONFIRMED"]
        ).exists()

        if existing_booking:
            raise serializers.ValidationError("Seat is already booked")

        # Check if trip is bookable
        if not trip.is_bookable():
            raise serializers.ValidationError("Trip is not available for booking")

        # Payment validation
        payment_method = attrs.get("payment_method")
        if payment_method == "MOBILE_MONEY":
            mm_number = self.initial_data.get("mobile_money_number", "").strip()
            mm_provider = self.initial_data.get("mobile_money_provider", "").strip()
            if not mm_number or not mm_provider:
                raise serializers.ValidationError(
                    "Mobile Money number and provider are required for MOBILE_MONEY payments"
                )
            # Store cleaned values in attrs for create
            attrs["mobile_money_number"] = mm_number
            attrs["mobile_money_provider"] = mm_provider

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        trip = validated_data["trip"]
        seat = validated_data[
            "seat"
        ]  # This will now be present due to validation logic

        # Calculate pricing
        base_fare = trip.base_fare
        seat_fee = base_fare * (seat.price_multiplier - 1)
        service_fee = 0  # No service fee for direct bookings
        total_amount = base_fare + seat_fee + service_fee

        # Create booking
        booking = Booking.objects.create(
            company=request.user.company,
            trip=trip,
            passenger=request.user,  # Temporary - will be updated if passenger account exists
            seat=seat,
            status="CONFIRMED",  # Direct bookings are immediately confirmed
            source="DIRECT",
            passenger_name=validated_data["passenger_name"],
            passenger_phone=validated_data["passenger_phone"],
            passenger_email=validated_data.get("passenger_email", ""),
            base_fare=base_fare,
            seat_fee=seat_fee,
            service_fee=service_fee,
            total_amount=total_amount,
            booked_by=request.user,
        )

        # Confirm the booking
        booking.confirm_booking()

        # Create a payment record based on selected method
        payment_status = (
            "COMPLETED"
            if self.validated_data.get("payment_method") == "CASH"
            else "PENDING"
        )
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=total_amount,
            payment_method=self.validated_data.get("payment_method"),
            status=payment_status,
            mobile_money_number=self.validated_data.get("mobile_money_number", ""),
            mobile_money_provider=self.validated_data.get("mobile_money_provider", ""),
        )
        if payment.status == "COMPLETED":
            payment.completed_at = timezone.now()
            payment.save()

        return booking


class BookingCancellationSerializer(serializers.ModelSerializer):
    """
    Booking cancellation serializer
    """

    class Meta:
        model = BookingCancellation
        fields = ("reason", "cancellation_fee", "refund_amount", "created_at")
        read_only_fields = ("cancellation_fee", "refund_amount", "created_at")


class BookingHistorySerializer(serializers.ModelSerializer):
    """
    Booking history serializer
    """

    performed_by_name = serializers.CharField(
        source="performed_by.get_full_name", read_only=True
    )

    class Meta:
        model = BookingHistory
        fields = ("action", "description", "performed_by_name", "created_at")
        read_only_fields = ("action", "description", "performed_by_name", "created_at")


class SeatReservationSerializer(serializers.ModelSerializer):
    """
    Seat reservation serializer
    """

    seat_number = serializers.CharField(source="seat.seat_number", read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = SeatReservation
        fields = (
            "id",
            "trip",
            "seat",
            "seat_number",
            "expires_at",
            "is_active",
            "is_expired",
        )
        read_only_fields = ("id", "expires_at", "is_expired")
