from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .mobile_serializers import (
    MobileUserSerializer,
    MobileTripSearchSerializer,
    MobileTripSerializer,
    MobileBookingCreateSerializer,
    MobileBookingSerializer,
    MobileSeatSerializer,
    MobileNotificationSerializer,
)
from trips.models import Trip, Route
from bookings.models import Booking
from companies.models import BusSeat
from accounts.models import PassengerProfile
from companies.models import Company

User = get_user_model()


class MobileTokenObtainPairView(TokenObtainPairView):
    """Mobile-optimized login with additional user data"""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Add user profile data to response
            user = User.objects.get(email=request.data.get("email"))
            user_data = MobileUserSerializer(user, context={"request": request}).data
            response.data["user"] = user_data

        return response


@api_view(["POST"])
@permission_classes([AllowAny])
def mobile_register(request):
    """Register new passenger account"""
    data = request.data

    # Validate required fields
    required_fields = ["email", "password", "first_name", "last_name", "phone_number"]
    for field in required_fields:
        if not data.get(field):
            return Response(
                {"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST
            )

    # Check if user already exists
    if User.objects.filter(email=data["email"]).exists():
        return Response(
            {"error": "User with this email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create user
    user = User.objects.create_user(
        email=data["email"],
        password=data["password"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data["phone_number"],
        user_type="PASSENGER",
    )

    # Create passenger profile
    PassengerProfile.objects.create(
        user=user,
        date_of_birth=data.get("date_of_birth"),
        emergency_contact=data.get("emergency_contact"),
        emergency_phone=data.get("emergency_phone"),
    )

    # Return user data
    serializer = MobileUserSerializer(user, context={"request": request})
    return Response(
        {"message": "Account created successfully", "user": serializer.data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def search_trips(request):
    """Search available trips for mobile app"""
    serializer = MobileTripSearchSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    departure_date = data["departure_date"]

    routes = Route.objects.filter(
        Q(origin_city__icontains=data["origin"])
        & Q(destination_city__icontains=data["destination"])
    )

    if not routes.exists():
        return Response(
            {"trips": [], "message": "No routes found for this destination"}
        )

    # Find trips for the date
    trips = (
        Trip.objects.filter(
            route__in=routes, departure_date=departure_date, status="SCHEDULED"
        )
        .select_related("company", "route", "bus")
        .prefetch_related("bus__seats")
    )

    # Filter by bus type if specified
    if data.get("bus_type"):
        trips = trips.filter(bus__bus_type=data["bus_type"])

    # Filter trips with available seats
    available_trips = []
    for trip in trips:
        booked_seats_count = Booking.objects.filter(
            trip=trip, status__in=["PENDING", "CONFIRMED"]
        ).count()
        available_seats = trip.bus.total_seats - booked_seats_count

        if available_seats >= data["passengers"]:
            available_trips.append(trip)

    # Serialize and return
    trip_serializer = MobileTripSerializer(
        available_trips, many=True, context={"request": request}
    )

    return Response(
        {"trips": trip_serializer.data, "total_found": len(available_trips)}
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def trip_details(request, trip_id):
    """Get detailed trip information including seat map"""
    try:
        trip = Trip.objects.select_related("company", "route", "bus").get(
            id=trip_id, status="SCHEDULED"
        )
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get trip details
    trip_data = MobileTripSerializer(trip, context={"request": request}).data

    # Get seat map (with pricing and availability based on trip context)
    seats = trip.bus.seats.all().order_by("row_number", "seat_position")
    seat_data = MobileSeatSerializer(seats, many=True, context={"trip": trip}).data

    return Response(
        {
            "trip": trip_data,
            "seats": seat_data,
            "seat_layout": {
                "rows": trip.bus.total_seats // 4,  # Assuming 4 seats per row
                "seats_per_row": 4,
            },
        }
    )


class MobileBookingCreateView(generics.CreateAPIView):
    """Create new booking from mobile app"""

    serializer_class = MobileBookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.save()

        # Return booking details
        booking_serializer = MobileBookingSerializer(
            booking, context={"request": request}
        )

        return Response(
            {
                "message": "Booking created successfully",
                "booking": booking_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class MobileBookingListView(generics.ListAPIView):
    """List user's bookings for mobile app"""

    serializer_class = MobileBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects.filter(passenger=self.request.user)
            .select_related("trip__company", "trip__route", "seat")
            .order_by("-created_at")
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_details(request, booking_id):
    """Get detailed booking information"""
    try:
        booking = Booking.objects.select_related(
            "trip__company", "trip__route", "seat"
        ).get(id=booking_id, passenger=request.user)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = MobileBookingSerializer(booking, context={"request": request})
    return Response({"booking": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """Cancel a booking from mobile app"""
    try:
        booking = Booking.objects.get(
            id=booking_id, passenger=request.user, status__in=["CONFIRMED", "PENDING"]
        )
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found or cannot be cancelled"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if cancellation is allowed (e.g., not too close to departure)
    departure_datetime = timezone.datetime.combine(
        booking.trip.departure_date, booking.trip.departure_time
    )
    departure_datetime = timezone.make_aware(departure_datetime)

    if departure_datetime - timezone.now() < timedelta(hours=2):
        return Response(
            {"error": "Cannot cancel booking less than 2 hours before departure"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Cancel booking
    booking.cancel_booking("Cancelled by passenger via mobile app")

    return Response({"message": "Booking cancelled successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get user profile for mobile app"""
    serializer = MobileUserSerializer(request.user, context={"request": request})
    return Response({"profile": serializer.data})


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile from mobile app"""
    user = request.user
    data = request.data

    # Update user fields
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.save()

    # Update passenger profile
    if hasattr(user, "passenger_profile"):
        profile = user.passenger_profile
        profile.date_of_birth = data.get("date_of_birth", profile.date_of_birth)
        profile.emergency_contact = data.get(
            "emergency_contact", profile.emergency_contact
        )
        profile.emergency_phone = data.get("emergency_phone", profile.emergency_phone)
        profile.preferred_payment_method = data.get(
            "preferred_payment_method", profile.preferred_payment_method
        )
        profile.save()

    serializer = MobileUserSerializer(user, context={"request": request})
    return Response(
        {"message": "Profile updated successfully", "profile": serializer.data}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device(request):
    """Register device for push notifications"""
    serializer = MobileNotificationSerializer(data=request.data)

    if serializer.is_valid():
        # Store device token (you might want to create a DeviceToken model)
        # For now, just return success
        return Response({"message": "Device registered successfully"})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def popular_routes(request):
    """Get popular routes for mobile app homepage"""
    popular_routes = (
        Route.objects.annotate(booking_count=Count("trips__bookings"))
        .filter(booking_count__gt=0, is_active=True)
        .order_by("-booking_count")[:10]
    )

    routes_data = []
    for route in popular_routes:
        routes_data.append(
            {
                "id": route.id,
                "origin": route.origin_city,
                "destination": route.destination_city,
                "distance": route.distance_km,
                "booking_count": route.booking_count,
                "base_fare": float(route.base_fare),
            }
        )

    return Response({"popular_routes": routes_data})
