import random
import string
from datetime import datetime, timezone as dt_timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from trips.models import Trip

from .models import Booking
from .serializers import BookingSerializer


def _generate_booking_reference():
    stamp = datetime.now(dt_timezone.utc).strftime('%Y%m%d%H%M')
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'BK{stamp}{suffix}'


def _check_object_access(user, booking):
    if user.user_type == 'SUPER_ADMIN':
        return True
    if user.user_type == 'COMPANY_STAFF':
        return user.company_id == booking.company_id
    return user.id == booking.passenger_id


class BookingViewSet(viewsets.ViewSet):

    def _base_queryset(self):
        return Booking.objects.select_related(
            'trip__route', 'trip__bus', 'seat', 'passenger',
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

        data = dict(request.data)
        data['company_id'] = trip.company_id
        data.setdefault('passenger_id', request.user.id)

        serializer = BookingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(booking_reference=_generate_booking_reference())
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

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        if not _check_object_access(request.user, booking):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        booking.status = 'CANCELLED'
        booking.cancelled_at = booking.cancelled_at or timezone.now()
        booking.save(update_fields=['status', 'cancelled_at', 'updated_at'])
        return Response({'data': BookingSerializer(booking).data})
