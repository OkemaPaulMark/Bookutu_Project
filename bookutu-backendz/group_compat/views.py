from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from companies.models import Company, Bus
from trips.models import Route, Trip
from .serializers import (
    CompatCompanySerializer,
    CompatBusSerializer,
    CompatRouteSerializer,
    CompatTripSerializer,
    CompatBookingCreateSerializer,
    CompatBookingSerializer,
)
from rest_framework.decorators import action
from bookings.models import Booking as CoreBooking


class CompatCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompatCompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'city', 'country']
    search_fields = ['name', 'registration_number']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'is_company_staff') and user.is_company_staff() and user.company:
            qs = qs.filter(id=user.company_id)
        return qs


class CompatBusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = CompatBusSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['company', 'status', 'bus_type']
    search_fields = ['license_plate', 'model', 'make']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'is_company_staff') and user.is_company_staff() and user.company:
            qs = qs.filter(company=user.company)
        return qs


class CompatRouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = CompatRouteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['company', 'is_active', 'origin_city', 'destination_city']
    search_fields = ['name', 'origin_city', 'destination_city']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'is_company_staff') and user.is_company_staff() and user.company:
            qs = qs.filter(company=user.company)
        return qs


class CompatTripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = CompatTripSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['company', 'route', 'bus', 'status', 'departure_date']
    search_fields = []

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'is_company_staff') and user.is_company_staff() and user.company:
            qs = qs.filter(company=user.company)
        return qs

    @action(detail=True, methods=['post'], url_path='book')
    def book(self, request, pk=None):
        trip = self.get_object()
        serializer = CompatBookingCreateSerializer(data=request.data, context={'request': request})
        serializer.initial_data['trip'] = trip.id
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response({
            'booking_reference': booking.booking_reference,
            'status': booking.status,
            'trip': booking.trip.id,
            'seat_number': booking.seat.seat_number,
            'passenger_name': booking.passenger_name,
            'passenger_phone': booking.passenger_phone,
            'total_amount': str(booking.total_amount),
        }, status=status.HTTP_201_CREATED)


class CompatBookingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CoreBooking.objects.all()
    serializer_class = CompatBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['trip', 'status', 'created_at']
    search_fields = ['booking_reference', 'passenger_name', 'passenger_phone']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'is_company_staff') and user.is_company_staff() and user.company:
            qs = qs.filter(company=user.company)
        else:
            qs = qs.filter(passenger=user)
        return qs

# Create your views here.
