import random
import string

from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from fleet.models import BusSeat
from trips.models import Trip

from .models import Booking
from .serializers import BookingSerializer


def _generate_booking_reference():
    while True:
        digits = ''.join(random.choices(string.digits, k=4))
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        reference = f'BK{digits}{letters}'
        if not Booking.objects.filter(booking_reference=reference).exists():
            return reference


def _check_object_access(user, booking):
    if user.user_type == 'SUPER_ADMIN':
        return True
    if user.user_type == 'COMPANY_STAFF':
        return user.company_id == booking.company_id
    return user.id == booking.passenger_id


class BookingViewSet(viewsets.ViewSet):

    def _base_queryset(self):
        return Booking.objects.select_related(
            'trip__route', 'trip__bus', 'trip__company', 'seat', 'passenger',
        ).prefetch_related('payments')

    def list(self, request):
        user = request.user
        queryset = self._base_queryset()

        if user.user_type == 'COMPANY_STAFF':
            queryset = queryset.filter(company_id=user.company_id)
        elif user.user_type == 'PASSENGER':
            queryset = queryset.filter(passenger_id=user.id)

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(booking_reference__icontains=search)
                | Q(passenger_name__icontains=search)
                | Q(passenger_phone__icontains=search)
            )

        serializer = BookingSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        booking = get_object_or_404(self._base_queryset(), pk=pk)
        if not _check_object_access(request.user, booking):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': BookingSerializer(booking).data})

    def create(self, request):
        trip_id = request.data.get('trip_id')
        if not trip_id:
            return Response({'detail': 'tripId is required.'}, status=status.HTTP_400_BAD_REQUEST)
        trip = get_object_or_404(Trip, pk=trip_id)

        if trip.status != 'SCHEDULED':
            return Response({'detail': 'This trip is not open for booking.'}, status=status.HTTP_400_BAD_REQUEST)

        seat_id = request.data.get('seat_id')
        if not seat_id:
            return Response({'detail': 'seatId is required.'}, status=status.HTTP_400_BAD_REQUEST)
        seat = get_object_or_404(BusSeat, pk=seat_id)
        if seat.bus_id != trip.bus_id:
            return Response({'detail': 'Seat does not belong to this trip\'s bus.'}, status=status.HTTP_400_BAD_REQUEST)

        already_booked = Booking.objects.filter(trip_id=trip.id, seat_id=seat.id).exclude(status='CANCELLED').exists()
        if already_booked:
            return Response({'detail': 'This seat is already booked for this trip.'}, status=status.HTTP_400_BAD_REQUEST)

        if trip.available_seats <= 0:
            return Response({'detail': 'No seats available on this trip.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        base_fare = trip.base_fare
        seat_fee = round(base_fare * (seat.price_multiplier - 1), 2) if seat.price_multiplier != 1 else 0
        service_fee = 0
        total_amount = base_fare + seat_fee + service_fee

        data = dict(request.data)
        data['company_id'] = trip.company_id
        data.setdefault('passenger_id', user.id)
        data.setdefault('passenger_name', f'{user.first_name} {user.last_name}'.strip() or user.email)
        data.setdefault('passenger_phone', user.phone_number or '')
        data.setdefault('passenger_email', user.email)

        serializer = BookingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(
            booking_reference=_generate_booking_reference(),
            base_fare=base_fare,
            seat_fee=seat_fee,
            service_fee=service_fee,
            total_amount=total_amount,
            status='CONFIRMED',
            confirmed_at=timezone.now(),
        )

        trip.booked_seats += 1
        trip.available_seats -= 1
        trip.save(update_fields=['booked_seats', 'available_seats', 'updated_at'])

        return Response({'data': BookingSerializer(booking).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        booking = get_object_or_404(Booking, pk=pk)
        if not _check_object_access(request.user, booking):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BookingSerializer(booking, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    def destroy(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        if request.user.user_type not in ('SUPER_ADMIN', 'COMPANY_STAFF'):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        if not _check_object_access(request.user, booking):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'CANCELLED':
            Trip.objects.filter(pk=booking.trip_id).update(
                booked_seats=F('booked_seats') - 1, available_seats=F('available_seats') + 1,
            )

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        if not _check_object_access(request.user, booking):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status == 'CANCELLED':
            return Response({'detail': 'This booking is already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'CANCELLED'
        booking.cancelled_at = booking.cancelled_at or timezone.now()
        booking.save(update_fields=['status', 'cancelled_at', 'updated_at'])

        Trip.objects.filter(pk=booking.trip_id).update(
            booked_seats=F('booked_seats') - 1, available_seats=F('available_seats') + 1,
        )

        return Response({'data': BookingSerializer(booking).data})
