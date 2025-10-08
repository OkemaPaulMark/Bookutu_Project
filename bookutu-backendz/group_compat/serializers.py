from rest_framework import serializers
from companies.models import Company, Bus
from trips.models import Route, Trip
from bookings.models import Booking as CoreBooking
from companies.models import BusSeat
from payments.models import Payment
from django.utils import timezone


class CompatCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'phone_number', 'address', 'city', 'state',
            'country', 'website', 'registration_number', 'status', 'created_at'
        ]


class CompatBusSerializer(serializers.ModelSerializer):
    bus_company = serializers.SerializerMethodField()
    number_plate = serializers.CharField(source='license_plate')
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = [
            'id', 'bus_company', 'number_plate', 'is_active', 'model', 'make',
            'year', 'total_seats', 'bus_type'
        ]

    def get_bus_company(self, obj):
        return obj.company_id

    def get_is_active(self, obj):
        return obj.status == 'ACTIVE'


class CompatRouteSerializer(serializers.ModelSerializer):
    bus_company = serializers.SerializerMethodField()
    start_location = serializers.CharField(source='origin')
    end_location = serializers.CharField(source='destination')

    class Meta:
        model = Route
        fields = [
            'id', 'bus_company', 'start_location', 'end_location', 'distance_km'
        ]

    def get_bus_company(self, obj):
        return obj.company_id


class CompatTripSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(read_only=True)
    bus = serializers.PrimaryKeyRelatedField(read_only=True)
    departure_time = serializers.DateTimeField(source='departure_datetime')
    arrival_time = serializers.DateTimeField(source='arrival_datetime')
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Trip
        fields = [
            'id', 'route', 'bus', 'departure_time', 'arrival_time', 'price'
        ]


class CompatBookingCreateSerializer(serializers.Serializer):
    # Align with group API expectations
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    seat_number = serializers.CharField()
    passenger_name = serializers.CharField(max_length=200)
    passenger_phone = serializers.CharField(max_length=20)
    payment_method = serializers.ChoiceField(choices=[
        ('mobile_money', 'mobile_money'),
        ('card', 'card'),
        ('cash', 'cash'),
    ], required=False)
    payment_status = serializers.ChoiceField(choices=[
        ('pending', 'pending'),
        ('paid', 'paid'),
        ('failed', 'failed'),
    ], required=False, default='pending')
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    payment_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, attrs):
        trip: Trip = attrs['trip']
        if not trip.is_bookable():
            raise serializers.ValidationError('Trip not available for booking')

        seat_number_raw = str(attrs['seat_number']).strip()
        # Try exact match; group might send integers
        possible_numbers = {seat_number_raw, str(seat_number_raw)}
        seat = BusSeat.objects.filter(bus=trip.bus, seat_number__in=possible_numbers).first()
        if not seat:
            raise serializers.ValidationError('Seat not found on this bus')

        # Ensure seat not already booked for this trip
        exists = CoreBooking.objects.filter(trip=trip, seat=seat, status__in=['PENDING', 'CONFIRMED']).exists()
        if exists:
            raise serializers.ValidationError('Seat already booked for this trip')

        attrs['seat'] = seat
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        trip: Trip = validated_data['trip']
        seat: BusSeat = validated_data['seat']
        passenger_name = validated_data['passenger_name']
        passenger_phone = validated_data['passenger_phone']

        # Price: use trip.base_fare; seat multipliers could apply later
        base_fare = trip.base_fare
        total_amount = base_fare

        booking = CoreBooking.objects.create(
            trip=trip,
            passenger=request.user,
            seat=seat,
            passenger_name=passenger_name,
            passenger_phone=passenger_phone,
            passenger_email=getattr(request.user, 'email', ''),
            base_fare=base_fare,
            seat_fee=0,
            service_fee=0,
            total_amount=total_amount,
            source='WEB',
            booked_by=request.user,
        )

        # Optional payment creation
        payment_method = validated_data.get('payment_method')
        payment_status = validated_data.get('payment_status', 'pending')
        amount_paid = validated_data.get('amount_paid', total_amount)
        payment_reference = validated_data.get('payment_reference', '')

        if payment_method:
            method_map = {
                'mobile_money': 'MOBILE_MONEY',
                'card': 'CARD',
                'cash': 'CASH',
            }
            status_map = {
                'pending': 'PENDING',
                'paid': 'COMPLETED',
                'failed': 'FAILED',
            }

            pay = Payment.objects.create(
                booking=booking,
                user=request.user,
                company=trip.company,
                amount=amount_paid,
                payment_method=method_map[payment_method],
                status=status_map[payment_status],
                gateway_transaction_id=payment_reference,
            )

            if pay.status == 'COMPLETED':
                booking.confirm_booking()

        return booking


class CompatBookingSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(read_only=True)
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    payment_status = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()

    class Meta:
        model = CoreBooking
        fields = [
            'id', 'booking_reference', 'status', 'trip', 'seat_number',
            'passenger_name', 'passenger_phone', 'total_amount',
            'payment_status', 'amount_paid', 'payment_method',
            'created_at'
        ]

    def get_payment_status(self, obj):
        latest = obj.payments.order_by('-created_at').first()
        if not latest:
            return 'pending'
        return {
            'PENDING': 'pending',
            'PROCESSING': 'pending',
            'COMPLETED': 'paid',
            'FAILED': 'failed',
            'CANCELLED': 'failed',
            'REFUNDED': 'paid',
        }.get(latest.status, 'pending')

    def get_amount_paid(self, obj):
        latest = obj.payments.order_by('-created_at').first()
        return str(latest.amount) if latest else '0'

    def get_payment_method(self, obj):
        latest = obj.payments.order_by('-created_at').first()
        if not latest:
            return None
        return {
            'MOBILE_MONEY': 'mobile_money',
            'CARD': 'card',
            'CASH': 'cash',
            'BANK_TRANSFER': 'cash',
            'WALLET': 'card',
        }.get(latest.payment_method, None)


