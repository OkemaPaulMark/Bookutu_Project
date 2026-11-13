from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
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


class MobileBookingPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 200


class MobileBookingListView(generics.ListAPIView):
    """List user's bookings for mobile app"""

    serializer_class = MobileBookingSerializer
    pagination_class = MobileBookingPagination
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


# ---------------------------------------------------------------------------
# Endpoints used by the Flutter app's booking, payment, map and notification
# screens.
# ---------------------------------------------------------------------------
from django.db import transaction
from rest_framework import serializers as drf_serializers
from payments.models import Payment
from notifications.models import Announcement
from .geo import route_path, interpolate, coords_for


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_bookings(request):
    """Book one or more seats on a trip in a single atomic request.

    Body: {"trip": <id>, "seat_numbers": ["1A", "1B"], "passenger_name"?, "passenger_phone"?}
    """
    seat_numbers = request.data.get("seat_numbers") or []
    if isinstance(seat_numbers, str):
        seat_numbers = [seat_numbers]
    if not seat_numbers:
        return Response({"error": "Select at least one seat"}, status=status.HTTP_400_BAD_REQUEST)

    bookings = []
    try:
        with transaction.atomic():
            for number in seat_numbers:
                ser = MobileBookingCreateSerializer(
                    data={
                        "trip": request.data.get("trip"),
                        "seat_number": number,
                        "passenger_name": request.data.get("passenger_name", ""),
                        "passenger_phone": request.data.get("passenger_phone", ""),
                    },
                    context={"request": request},
                )
                ser.is_valid(raise_exception=True)
                bookings.append(ser.save())
    except drf_serializers.ValidationError as e:
        detail = e.detail
        if isinstance(detail, dict):
            detail = detail.get("non_field_errors", detail)
        if isinstance(detail, list) and detail:
            detail = detail[0]
        return Response({"error": str(detail)}, status=status.HTTP_400_BAD_REQUEST)

    data = MobileBookingSerializer(bookings, many=True, context={"request": request}).data
    return Response(
        {"message": f"{len(bookings)} seat(s) reserved", "bookings": data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pay_bookings(request):
    """Pay for pending bookings and confirm them.

    This is a sandbox payment: no real money moves. It records a COMPLETED
    Payment and confirms the booking, so the rest of the system (company
    dashboard, manifests, seat availability) behaves as after a real payment.

    Body: {"booking_ids": [..], "method": "MTN"|"AIRTEL"|"CARD", "phone": "07..."}
    """
    ids = request.data.get("booking_ids") or []
    method = (request.data.get("method") or "MTN").upper()
    phone = request.data.get("phone") or getattr(request.user, "phone_number", "")
    bookings = list(
        Booking.objects.filter(id__in=ids, passenger=request.user, status="PENDING")
        .select_related("trip", "company")
    )
    if not bookings:
        return Response({"error": "No pending bookings to pay for"}, status=status.HTTP_400_BAD_REQUEST)

    is_card = method == "CARD"
    with transaction.atomic():
        for b in bookings:
            Payment.objects.create(
                booking=b,
                company=b.company,
                user=request.user,
                amount=b.total_amount,
                payment_method="CARD" if is_card else "MOBILE_MONEY",
                status="COMPLETED",
                mobile_money_number="" if is_card else phone,
                mobile_money_provider="" if is_card else ("Airtel" if method == "AIRTEL" else "MTN"),
                gateway_transaction_id=f"SANDBOX-{b.booking_reference}",
                gateway_response={"sandbox": True},
                completed_at=timezone.now(),
            )
            b.confirm_booking()

    refreshed = Booking.objects.filter(id__in=[b.id for b in bookings])
    return Response({
        "message": "Payment successful",
        "bookings": MobileBookingSerializer(refreshed, many=True, context={"request": request}).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    return Response({"profile": MobileUserSerializer(request.user, context={"request": request}).data})


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    user = request.user
    for field in ("first_name", "last_name", "phone_number"):
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()
    return Response({
        "message": "Profile updated successfully",
        "profile": MobileUserSerializer(user, context={"request": request}).data,
    })


def _trip_progress(trip, now):
    dep = timezone.make_aware(timezone.datetime.combine(trip.departure_date, trip.departure_time))
    arr = timezone.make_aware(timezone.datetime.combine(trip.departure_date, trip.arrival_time))
    total = (arr - dep).total_seconds() or 1
    return (now - dep).total_seconds() / total, dep, arr


@api_view(["GET"])
@permission_classes([AllowAny])
def map_data(request):
    """Terminals, active routes and live bus positions for the map screen.

    Bus positions are estimated from each trip's schedule along its route
    (no GPS hardware is wired in yet).
    """
    now = timezone.localtime()
    today = now.date()

    trips = (
        Trip.objects.filter(departure_date=today)
        .exclude(status__in=["CANCELLED", "COMPLETED"])
        .select_related("route", "bus", "company")
    )

    buses, routes, terminals = [], {}, {}
    for trip in trips:
        path = route_path(trip.route)
        if len(path) < 2:
            continue
        progress, dep, arr = _trip_progress(trip, now)
        routes.setdefault(trip.route_id, {
            "id": trip.route_id,
            "name": f"{trip.route.origin_city} → {trip.route.destination_city}",
            "points": [{"lat": p[0], "lng": p[1]} for p in path],
        })
        for city, terminal in ((trip.route.origin_city, trip.route.origin_terminal),
                               (trip.route.destination_city, trip.route.destination_terminal)):
            c = coords_for(city)
            if c:
                terminals.setdefault(city.lower(), {"city": city, "name": terminal or city,
                                                    "lat": c[0], "lng": c[1]})
        if progress > 1:
            continue  # already arrived
        if progress < 0:
            state, pos = "WAITING", path[0]
        else:
            state, pos = "IN_TRANSIT", interpolate(path, progress)
        buses.append({
            "trip_id": trip.id,
            "company": trip.company.name,
            "plate": trip.bus.license_plate,
            "route": f"{trip.route.origin_city} → {trip.route.destination_city}",
            "state": state,
            "progress": round(max(progress, 0) * 100),
            "departure_time": trip.departure_time.strftime("%H:%M"),
            "arrival_time": trip.arrival_time.strftime("%H:%M"),
            "lat": pos[0],
            "lng": pos[1],
        })

    return Response({
        "generated_at": now.isoformat(),
        "buses": buses,
        "routes": list(routes.values()),
        "terminals": list(terminals.values()),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def notifications_feed(request):
    """Announcements for passengers, plus booking updates when logged in."""
    items = []
    for a in Announcement.objects.filter(is_active=True, target_audience__in=["all", "passengers"]).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )[:20]:
        items.append({"type": "announcement", "title": a.title, "message": a.message,
                      "priority": a.priority, "created_at": a.created_at})
    if request.user.is_authenticated:
        for b in Booking.objects.filter(passenger=request.user).select_related(
                "trip__route").order_by("-updated_at")[:10]:
            r = b.trip.route
            items.append({
                "type": "booking",
                "title": f"Booking {b.get_status_display().lower()}",
                "message": f"{r.origin_city} → {r.destination_city} on {b.trip.departure_date:%d %b} "
                           f"at {b.trip.departure_time:%H:%M}, seat {b.seat.seat_number if b.seat else '-'} "
                           f"({b.booking_reference})",
                "priority": "medium",
                "created_at": b.updated_at,
            })
    items.sort(key=lambda i: i["created_at"], reverse=True)
    return Response({"notifications": items})
