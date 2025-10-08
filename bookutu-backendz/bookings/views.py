from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import Booking, BookingHistory, BookingCancellation
from .serializers import BookingSerializer, BookingHistorySerializer, BookingCancellationSerializer
from accounts.permissions import IsCompanyStaff, IsSameCompany
from trips.models import Trip


class BookingListView(generics.ListAPIView):
    """
    Company booking list with filtering
    """
    serializer_class = BookingSerializer
    permission_classes = [IsCompanyStaff]
    filterset_fields = ['status', 'source', 'trip__departure_date']
    search_fields = ['booking_reference', 'passenger_name', 'passenger_phone']
    ordering_fields = ['created_at', 'trip__departure_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Booking.objects.filter(
            company=self.request.user.company
        ).select_related('trip', 'seat', 'passenger')


class BookingDetailView(generics.RetrieveAPIView):
    """
    Company booking detail view
    """
    serializer_class = BookingSerializer
    permission_classes = [IsCompanyStaff, IsSameCompany]
    
    def get_queryset(self):
        return Booking.objects.filter(company=self.request.user.company)


class BookingCancelView(APIView):
    """
    Cancel a booking
    """
    permission_classes = [IsCompanyStaff]
    
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(
                id=pk,
                company=request.user.company
            )
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if booking.status != 'CONFIRMED':
            return Response({
                'error': 'Only confirmed bookings can be cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('reason', 'Cancelled by company staff')
        
        # Calculate cancellation fee
        cancellation_fee = booking.calculate_cancellation_fee()
        refund_amount = booking.total_amount - cancellation_fee
        
        # Cancel the booking
        booking.cancel_booking(reason)
        
        # Create cancellation record
        cancellation = BookingCancellation.objects.create(
            booking=booking,
            reason=reason,
            cancelled_by=request.user,
            cancellation_fee=cancellation_fee,
            refund_amount=refund_amount
        )
        
        return Response({
            'message': 'Booking cancelled successfully',
            'cancellation_fee': float(cancellation_fee),
            'refund_amount': float(refund_amount),
            'booking_status': booking.status
        })


class BookingHistoryView(generics.ListAPIView):
    """
    Booking history view
    """
    serializer_class = BookingHistorySerializer
    permission_classes = [IsCompanyStaff]
    
    def get_queryset(self):
        booking_id = self.kwargs['pk']
        return BookingHistory.objects.filter(
            booking_id=booking_id,
            booking__company=self.request.user.company
        )


@api_view(['GET'])
@permission_classes([IsCompanyStaff])
def company_booking_manifest(request):
    """
    Get booking manifest for company trips
    """
    company = request.user.company
    trip_id = request.query_params.get('trip_id')
    departure_date = request.query_params.get('departure_date')
    
    filters = {'company': company}
    
    if trip_id:
        filters['trip_id'] = trip_id
    
    if departure_date:
        try:
            date = timezone.datetime.strptime(departure_date, '%Y-%m-%d').date()
            filters['trip__departure_date'] = date
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    bookings = Booking.objects.filter(
        **filters,
        status='CONFIRMED'
    ).select_related('trip', 'seat', 'passenger').order_by(
        'trip__departure_date',
        'trip__departure_time',
        'seat__row_number',
        'seat__seat_number'
    )
    
    # Group bookings by trip
    manifest_data = {}
    for booking in bookings:
        trip_key = f"{booking.trip.id}"
        
        if trip_key not in manifest_data:
            manifest_data[trip_key] = {
                'trip_info': {
                    'id': booking.trip.id,
                    'route': f"{booking.trip.route.origin_city} → {booking.trip.route.destination_city}",
                    'departure_date': booking.trip.departure_date,
                    'departure_time': booking.trip.departure_time,
                    'bus_registration': booking.trip.bus.registration_number,
                    'driver_name': booking.trip.driver_name,
                    'driver_phone': booking.trip.driver_phone
                },
                'passengers': [],
                'summary': {
                    'total_passengers': 0,
                    'total_revenue': 0,
                    'payment_methods': {}
                }
            }
        
        # Add passenger to manifest
        manifest_data[trip_key]['passengers'].append({
            'booking_reference': booking.booking_reference,
            'passenger_name': booking.passenger_name,
            'passenger_phone': booking.passenger_phone,
            'seat_number': booking.seat.seat_number,
            'seat_type': booking.seat.seat_type,
            'amount_paid': float(booking.total_amount),
            'booking_source': booking.source,
            'created_at': booking.created_at
        })
        
        # Update summary
        manifest_data[trip_key]['summary']['total_passengers'] += 1
        manifest_data[trip_key]['summary']['total_revenue'] += float(booking.total_amount)
    
    return Response({
        'manifest': list(manifest_data.values()),
        'total_trips': len(manifest_data)
    })
