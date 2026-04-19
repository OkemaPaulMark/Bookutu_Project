from rest_framework import generics, permissions #type:ignore
from rest_framework.decorators import api_view, permission_classes #type:ignore
from rest_framework.response import Response #type:ignore
from rest_framework.views import APIView #type:ignore
from django.utils import timezone #type:ignore
from django.db.models import Count, Sum, Q #type:ignore
from .models import Route, Trip
from .serializers import RouteSerializer, TripSerializer, TripManifestSerializer
from accounts.permissions import IsCompanyStaff, IsSameCompany
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from .models import Trip
from .serializers import TripSerializer, TripPublicSerializer
from rest_framework import generics, permissions, authentication


class RouteListCreateView(generics.ListCreateAPIView):
    """
    Route management - list and create routes
    """
    serializer_class = RouteSerializer
    permission_classes = [IsCompanyStaff]
    
    def get_queryset(self):
        return Route.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Route detail management
    """
    serializer_class = RouteSerializer
    permission_classes = [IsCompanyStaff, IsSameCompany]
    
    def get_queryset(self):
        return Route.objects.filter(company=self.request.user.company)


class TripListCreateView(generics.ListCreateAPIView):
    """
    Trip management - list and create trips
    """
    serializer_class = TripSerializer
    permission_classes = [IsCompanyStaff]
    filterset_fields = ['status', 'departure_date', 'route']
    ordering_fields = ['departure_date', 'departure_time', 'created_at']
    ordering = ['departure_date', 'departure_time']
    
    def get_queryset(self):
        return Trip.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Trip detail management
    """
    serializer_class = TripSerializer
    permission_classes = [IsCompanyStaff, IsSameCompany]
    
    def get_queryset(self):
        return Trip.objects.filter(company=self.request.user.company)


class TripManifestView(APIView):
    """
    Trip manifest - passenger list for a specific trip
    """
    permission_classes = [IsCompanyStaff]
    
    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id, company=request.user.company)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=404)
        
        # Get all confirmed bookings for this trip
        bookings = Booking.objects.filter(
            trip=trip,
            status='CONFIRMED'
        ).select_related('seat', 'passenger').order_by('seat__row_number', 'seat__seat_number')
        
        passengers = []
        total_revenue = 0
        
        for booking in bookings:
            passengers.append({
                'booking_reference': booking.booking_reference,
                'passenger_name': booking.passenger_name,
                'passenger_phone': booking.passenger_phone,
                'seat_number': booking.seat.seat_number,
                'seat_type': booking.seat.seat_type,
                'amount_paid': booking.total_amount,
                'booking_source': booking.source,
                'created_at': booking.created_at
            })
            total_revenue += booking.total_amount
        
        manifest_data = {
            'trip_id': trip.id,
            'trip_details': TripSerializer(trip).data,
            'passengers': passengers,
            'total_passengers': len(passengers),
            'total_revenue': total_revenue
        }
        
        serializer = TripManifestSerializer(manifest_data)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsCompanyStaff])
def trip_dashboard_stats(request):
    """
    Trip dashboard statistics
    """
    company = request.user.company
    today = timezone.now().date()
    
    stats = {
        'total_trips': Trip.objects.filter(company=company).count(),
        'scheduled_trips': Trip.objects.filter(
            company=company,
            status='SCHEDULED',
            departure_date__gte=today
        ).count(),
        'completed_trips': Trip.objects.filter(
            company=company,
            status='COMPLETED'
        ).count(),
        'cancelled_trips': Trip.objects.filter(
            company=company,
            status='CANCELLED'
        ).count(),
        'today_trips': Trip.objects.filter(
            company=company,
            departure_date=today
        ).count(),
        'active_routes': Route.objects.filter(
            company=company,
            is_active=True
        ).count()
    }
    
    return Response(stats)


class TripListCreateAPIView(generics.ListCreateAPIView):
    queryset = Trip.objects.all().select_related('route', 'bus', 'company')
    serializer_class = TripSerializer
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication]
    permission_classes = []  # override global IsAuthenticated

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TripPublicSerializer
        return TripSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)
        
    def get_authenticators(self):
        if self.request.method == 'GET':
            return []  # no authentication for GET
        return super().get_authenticators()

class PublicTripListAPIView(generics.ListAPIView):
    """
    Public endpoint — list all scheduled trips for Flutter
    """
    queryset = Trip.objects.filter(status='SCHEDULED').select_related('route', 'bus')
    serializer_class = TripPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # You can later filter by route, date, etc. e.g. ?route_id=1
        queryset = super().get_queryset()
        route_id = self.request.query_params.get('route_id')
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        return queryset
