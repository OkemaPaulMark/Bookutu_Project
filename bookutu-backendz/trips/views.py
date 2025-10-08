from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count, Sum, Q
from .models import Route, Trip
from .serializers import RouteSerializer, TripSerializer, TripManifestSerializer
from accounts.permissions import IsCompanyStaff, IsSameCompany
from bookings.models import Booking
from bookings.serializers import BookingSerializer


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
