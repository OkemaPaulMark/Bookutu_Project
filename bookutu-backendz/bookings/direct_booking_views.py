from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.contrib.auth import get_user_model
from .models import Booking, SeatReservation
from .serializers import DirectBookingSerializer, BookingSerializer
from companies.models import BusSeat
from trips.models import Trip, Route
from accounts.permissions import CanCreateDirectBooking
from .utils import generate_ticket, send_sms_ticket
import uuid

User = get_user_model()


class DirectBookingTripsView(APIView):
    """
    Get available trips for direct booking
    """
    permission_classes = [CanCreateDirectBooking]
    
    def get(self, request):
        company = request.user.company
        route_id = request.query_params.get('route_id')
        departure_date = request.query_params.get('departure_date')
        
        if not route_id or not departure_date:
            return Response({
                'error': 'route_id and departure_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            departure_date = timezone.datetime.strptime(departure_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get available trips for the route and date
        trips = Trip.objects.filter(
            company=company,
            route_id=route_id,
            departure_date=departure_date,
            status='SCHEDULED'
        ).filter(
            # Only trips that are bookable
            departure_date__gte=timezone.now().date()
        ).order_by('departure_time')
        
        trips_data = []
        for trip in trips:
            if trip.remaining_seats > 0:
                trips_data.append({
                    'id': trip.id,
                    'departure_time': trip.departure_time,
                    'arrival_time': trip.arrival_time,
                    'bus_registration': trip.bus.registration_number,
                    'bus_type': trip.bus.bus_type,
                    'available_seats': trip.remaining_seats,
                    'total_seats': trip.available_seats,
                    'base_fare': trip.base_fare,
                    'driver_name': trip.driver_name,
                    'features': {
                        'has_ac': trip.bus.has_ac,
                        'has_wifi': trip.bus.has_wifi,
                        'has_charging_ports': trip.bus.has_charging_ports,
                        'has_entertainment': trip.bus.has_entertainment,
                        'has_restroom': trip.bus.has_restroom
                    }
                })
        
        return Response({'trips': trips_data})


class DirectBookingSeatsView(APIView):
    """
    Get available seats for a specific trip
    """
    permission_classes = [CanCreateDirectBooking]
    
    def get(self, request, trip_id):
        company = request.user.company
        
        try:
            trip = Trip.objects.get(id=trip_id, company=company)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all seats for the bus
        all_seats = trip.bus.seats.all().order_by('row_number', 'seat_position')
        
        # Get booked seats
        booked_seats = set(
            Booking.objects.filter(
                trip=trip,
                status__in=['PENDING', 'CONFIRMED']
            ).values_list('seat_id', flat=True)
        )
        
        # Get temporarily reserved seats (not expired)
        reserved_seats = set(
            SeatReservation.objects.filter(
                trip=trip,
                is_active=True,
                expires_at__gt=timezone.now()
            ).exclude(
                user=request.user  # Allow user to see their own reservations
            ).values_list('seat_id', flat=True)
        )
        
        seats_data = []
        for seat in all_seats:
            seat_status = 'available'
            if seat.id in booked_seats:
                seat_status = 'booked'
            elif seat.id in reserved_seats:
                seat_status = 'reserved'
            
            seats_data.append({
                'id': seat.id,
                'seat_number': seat.seat_number,
                'row_number': seat.row_number,
                'seat_position': seat.seat_position,
                'seat_type': seat.seat_type,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
                'has_extra_legroom': seat.has_extra_legroom,
                'price_multiplier': seat.price_multiplier,
                'status': seat_status,
                'price': float(trip.base_fare * seat.price_multiplier)
            })
        
        # Group seats by row for better visualization
        seats_by_row = {}
        for seat in seats_data:
            row = seat['row_number']
            if row not in seats_by_row:
                seats_by_row[row] = []
            seats_by_row[row].append(seat)
        
        return Response({
            'trip_id': trip.id,
            'bus_registration': trip.bus.registration_number,
            'total_seats': trip.bus.total_seats,
            'available_seats': trip.remaining_seats,
            'seats': seats_data,
            'seats_by_row': seats_by_row
        })


class SeatReservationView(APIView):
    """
    Reserve a seat temporarily during booking process
    """
    permission_classes = [CanCreateDirectBooking]
    
    def post(self, request):
        trip_id = request.data.get('trip_id')
        seat_id = request.data.get('seat_id')
        
        if not trip_id or not seat_id:
            return Response({
                'error': 'trip_id and seat_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            trip = Trip.objects.get(id=trip_id, company=request.user.company)
            seat = BusSeat.objects.get(id=seat_id, bus=trip.bus)
        except (Trip.DoesNotExist, BusSeat.DoesNotExist):
            return Response({'error': 'Trip or seat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if seat is already booked
        if Booking.objects.filter(
            trip=trip,
            seat=seat,
            status__in=['PENDING', 'CONFIRMED']
        ).exists():
            return Response({'error': 'Seat is already booked'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if seat is already reserved by someone else
        existing_reservation = SeatReservation.objects.filter(
            trip=trip,
            seat=seat,
            is_active=True,
            expires_at__gt=timezone.now()
        ).exclude(user=request.user).first()
        
        if existing_reservation:
            return Response({'error': 'Seat is temporarily reserved'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update reservation
        reservation, created = SeatReservation.objects.update_or_create(
            trip=trip,
            seat=seat,
            user=request.user,
            defaults={
                'is_active': True,
                'expires_at': timezone.now() + timezone.timedelta(minutes=15)
            }
        )
        
        return Response({
            'message': 'Seat reserved successfully',
            'reservation_id': reservation.id,
            'expires_at': reservation.expires_at
        })
    
    def delete(self, request):
        """Release seat reservation"""
        trip_id = request.data.get('trip_id')
        seat_id = request.data.get('seat_id')
        
        SeatReservation.objects.filter(
            trip_id=trip_id,
            seat_id=seat_id,
            user=request.user
        ).update(is_active=False)
        
        return Response({'message': 'Seat reservation released'})


class DirectBookingCreateView(APIView):
    """
    Create a direct booking
    """
    permission_classes = [CanCreateDirectBooking]
    
    def post(self, request):
        serializer = DirectBookingSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            booking = serializer.save()
            
            # Release any seat reservations for this user and trip
            SeatReservation.objects.filter(
                trip=booking.trip,
                user=request.user
            ).update(is_active=False)
            
            # Generate ticket
            ticket_data = generate_ticket(booking)
            
            # Send SMS if phone number provided
            if booking.passenger_phone:
                sms_sent = send_sms_ticket(booking, ticket_data)
            else:
                sms_sent = False
            
            response_data = BookingSerializer(booking).data
            response_data.update({
                'ticket': ticket_data,
                'sms_sent': sms_sent,
                'message': 'Direct booking created successfully'
            })
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectBookingRoutesView(APIView):
    """
    Get available routes for direct booking
    """
    permission_classes = [CanCreateDirectBooking]
    
    def get(self, request):
        company = request.user.company
        
        # Get routes with upcoming trips
        routes = Route.objects.filter(
            company=company,
            is_active=True,
            trips__departure_date__gte=timezone.now().date(),
            trips__status='SCHEDULED'
        ).distinct().order_by('origin_city', 'destination_city')
        
        routes_data = []
        for route in routes:
            # Count upcoming trips for this route
            upcoming_trips = route.trips.filter(
                departure_date__gte=timezone.now().date(),
                status='SCHEDULED'
            ).count()
            
            routes_data.append({
                'id': route.id,
                'name': route.name,
                'origin_city': route.origin_city,
                'origin_terminal': route.origin_terminal,
                'destination_city': route.destination_city,
                'destination_terminal': route.destination_terminal,
                'distance_km': route.distance_km,
                'estimated_duration_hours': route.estimated_duration_hours,
                'base_fare': route.base_fare,
                'upcoming_trips': upcoming_trips,
                'route_display': f"{route.origin_city} → {route.destination_city}"
            })
        
        return Response({'routes': routes_data})


@api_view(['POST'])
@permission_classes([CanCreateDirectBooking])
def print_ticket(request, booking_id):
    """
    Generate printable ticket for direct booking
    """
    try:
        booking = Booking.objects.get(
            id=booking_id,
            company=request.user.company
        )
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate ticket data for printing
    ticket_data = generate_ticket(booking, format='print')
    
    return Response({
        'ticket': ticket_data,
        'message': 'Ticket ready for printing'
    })


@api_view(['POST'])
@permission_classes([CanCreateDirectBooking])
def resend_sms_ticket(request, booking_id):
    """
    Resend SMS ticket for direct booking
    """
    try:
        booking = Booking.objects.get(
            id=booking_id,
            company=request.user.company
        )
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not booking.passenger_phone:
        return Response({'error': 'No phone number available'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate and send SMS ticket
    ticket_data = generate_ticket(booking)
    sms_sent = send_sms_ticket(booking, ticket_data)
    
    return Response({
        'message': 'SMS ticket sent successfully' if sms_sent else 'Failed to send SMS',
        'sms_sent': sms_sent
    })


@api_view(['GET'])
@permission_classes([CanCreateDirectBooking])
def direct_booking_stats(request):
    """
    Get direct booking statistics for company dashboard
    """
    company = request.user.company
    today = timezone.now().date()
    
    stats = {
        'today_direct_bookings': Booking.objects.filter(
            company=company,
            source='DIRECT',
            created_at__date=today
        ).count(),
        'total_direct_bookings': Booking.objects.filter(
            company=company,
            source='DIRECT'
        ).count(),
        'direct_booking_revenue_today': float(
            Booking.objects.filter(
                company=company,
                source='DIRECT',
                created_at__date=today,
                status='CONFIRMED'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        ),
        'staff_performance': []
    }
    
    # Get staff performance for direct bookings
    staff_performance = User.objects.filter(
        company=company,
        user_type='COMPANY_STAFF'
    ).annotate(
        direct_bookings_count=Count(
            'created_bookings',
            filter=Q(created_bookings__source='DIRECT')
        ),
        direct_bookings_revenue=Sum(
            'created_bookings__total_amount',
            filter=Q(
                created_bookings__source='DIRECT',
                created_bookings__status='CONFIRMED'
            )
        )
    ).order_by('-direct_bookings_count')
    
    for staff in staff_performance:
        stats['staff_performance'].append({
            'staff_name': staff.get_full_name(),
            'bookings_count': staff.direct_bookings_count,
            'revenue': float(staff.direct_bookings_revenue or 0)
        })
    
    return Response(stats)
