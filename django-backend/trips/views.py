from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.models import Booking
from fleet.models import Bus, Driver, Route

from .models import Trip
from .serializers import TripSerializer


def _resolve_company_id(request):
    if request.user.user_type == 'COMPANY_STAFF':
        return request.user.company_id, None
    company_id = request.data.get('company_id')
    if not company_id:
        return None, Response({'detail': 'companyId is required.'}, status=status.HTTP_400_BAD_REQUEST)
    return company_id, None


def _update_payload(request):
    if request.user.user_type == 'SUPER_ADMIN':
        return request.data
    return {key: value for key, value in request.data.items() if key != 'company_id'}


def _check_object_access(user, trip):
    if user.user_type == 'SUPER_ADMIN':
        return True
    if user.user_type == 'PASSENGER':
        return trip.status == 'SCHEDULED'
    return user.company_id == trip.company_id


class TripViewSet(viewsets.ViewSet):

    def list(self, request):
        user = request.user
        queryset = Trip.objects.select_related('company', 'route', 'bus', 'driver')

        if user.user_type == 'COMPANY_STAFF':
            queryset = queryset.filter(company_id=user.company_id)
        elif user.user_type == 'PASSENGER':
            queryset = queryset.filter(status=request.query_params.get('status') or 'SCHEDULED')
        elif request.query_params.get('status'):
            queryset = queryset.filter(status=request.query_params['status'])

        if request.query_params.get('routeId'):
            queryset = queryset.filter(route_id=request.query_params['routeId'])
        if request.query_params.get('departureDate'):
            queryset = queryset.filter(departure_date__date=request.query_params['departureDate'])

        serializer = TripSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        trip = get_object_or_404(Trip.objects.select_related('company', 'route', 'bus', 'driver'), pk=pk)
        if not _check_object_access(request.user, trip):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': TripSerializer(trip).data})

    def create(self, request):
        if request.user.user_type not in ('SUPER_ADMIN', 'COMPANY_STAFF'):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        company_id, error = _resolve_company_id(request)
        if error:
            return error

        bus_id = request.data.get('bus_id')
        route_id = request.data.get('route_id')
        if not bus_id or not route_id:
            return Response({'detail': 'routeId and busId are required.'}, status=status.HTTP_400_BAD_REQUEST)

        bus = get_object_or_404(Bus, pk=bus_id)
        if bus.company_id != company_id:
            return Response({'detail': 'Invalid bus for company.'}, status=status.HTTP_400_BAD_REQUEST)

        route = get_object_or_404(Route, pk=route_id)
        if route.company_id != company_id:
            return Response({'detail': 'Invalid route for company.'}, status=status.HTTP_400_BAD_REQUEST)

        data = dict(request.data)
        data['company_id'] = company_id
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        trip = serializer.save(available_seats=bus.total_seats, booked_seats=0, status='SCHEDULED')
        return Response({'data': TripSerializer(trip).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        trip = get_object_or_404(Trip, pk=pk)
        if request.user.user_type not in ('SUPER_ADMIN', 'COMPANY_STAFF') or not _check_object_access(request.user, trip):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TripSerializer(trip, data=_update_payload(request), partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    @action(detail=False, methods=['get'], url_path='dashboard/stats')
    def dashboard_stats(self, request):
        company_id = request.user.company_id or request.query_params.get('companyId')
        if not company_id:
            return Response({'data': {
                'total_trips': 0, 'scheduled_trips': 0, 'completed_trips': 0, 'cancelled_trips': 0, 'today_trips': 0,
                'total_revenue': 0, 'total_bookings': 0, 'confirmed_bookings': 0, 'pending_bookings': 0, 'cancelled_bookings': 0,
                'fleet': {'active': 0, 'maintenance': 0, 'inactive': 0, 'total': 0},
                'active_routes': 0, 'active_drivers': 0, 'route_performance': [], 'monthly_revenue': [],
            }})

        confirmed_completed = ['CONFIRMED', 'COMPLETED']
        trips_qs = Trip.objects.filter(company_id=company_id)
        bookings_qs = Booking.objects.filter(company_id=company_id)
        today = timezone.localdate()

        revenue_agg = bookings_qs.filter(status__in=confirmed_completed).aggregate(total=Sum('total_amount'), count=Count('id'))
        buses_by_status = dict(
            Bus.objects.filter(company_id=company_id).values_list('status').annotate(c=Count('id')).values_list('status', 'c')
        )

        route_map = {}
        route_trips = Trip.objects.filter(company_id=company_id).select_related('route').prefetch_related('bookings')
        for trip in route_trips:
            label = f'{trip.route.origin_city} → {trip.route.destination_city}'
            confirmed_bookings = [b for b in trip.bookings.all() if b.status in confirmed_completed]
            entry = route_map.setdefault(trip.route_id, {'route': label, 'trips': 0, 'revenue': 0.0, 'booked_seats': 0})
            entry['trips'] += 1
            entry['revenue'] += sum(float(b.total_amount) for b in confirmed_bookings)
            entry['booked_seats'] += len(confirmed_bookings)
        route_performance = sorted(route_map.values(), key=lambda r: r['revenue'], reverse=True)[:5]

        six_months_ago = (timezone.now() - timezone.timedelta(days=180)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_map = {}
        for booking in bookings_qs.filter(status__in=confirmed_completed, created_at__gte=six_months_ago).values('created_at', 'total_amount'):
            key = booking['created_at'].strftime('%Y-%m')
            monthly_map[key] = monthly_map.get(key, 0) + float(booking['total_amount'])
        monthly_revenue = [{'month': month, 'revenue': revenue} for month, revenue in sorted(monthly_map.items())]

        return Response({'data': {
            'total_trips': trips_qs.count(),
            'scheduled_trips': trips_qs.filter(status='SCHEDULED').count(),
            'completed_trips': trips_qs.filter(status='COMPLETED').count(),
            'cancelled_trips': trips_qs.filter(status='CANCELLED').count(),
            'today_trips': trips_qs.filter(departure_date__date=today).count(),
            'total_revenue': float(revenue_agg['total'] or 0),
            'total_bookings': revenue_agg['count'] or 0,
            'confirmed_bookings': bookings_qs.filter(status='CONFIRMED').count(),
            'pending_bookings': bookings_qs.filter(status='PENDING').count(),
            'cancelled_bookings': bookings_qs.filter(status='CANCELLED').count(),
            'fleet': {
                'active': buses_by_status.get('ACTIVE', 0),
                'maintenance': buses_by_status.get('MAINTENANCE', 0),
                'inactive': buses_by_status.get('INACTIVE', 0),
                'total': sum(buses_by_status.values()),
            },
            'active_routes': Route.objects.filter(company_id=company_id, is_active=True).count(),
            'active_drivers': Driver.objects.filter(company_id=company_id, status='ACTIVE').count(),
            'route_performance': route_performance,
            'monthly_revenue': monthly_revenue,
        }})

    @action(detail=True, methods=['get'], url_path='manifest')
    def manifest(self, request, pk=None):
        trip = get_object_or_404(Trip.objects.select_related('route', 'bus'), pk=pk)
        if not _check_object_access(request.user, trip):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        bookings = list(trip.bookings.filter(status='CONFIRMED').select_related('seat').order_by('created_at'))
        total_revenue = sum(float(b.total_amount) for b in bookings)

        return Response({
            'trip_id': trip.id,
            'trip_details': {
                'route': f'{trip.route.origin_city} -> {trip.route.destination_city}',
                'departure_date': trip.departure_date,
                'departure_time': trip.departure_time,
                'bus': trip.bus.license_plate,
            },
            'passengers': [
                {
                    'booking_reference': b.booking_reference,
                    'passenger_name': b.passenger_name,
                    'passenger_phone': b.passenger_phone,
                    'seat_number': b.seat.seat_number,
                    'amount_paid': float(b.total_amount),
                }
                for b in bookings
            ],
            'total_passengers': len(bookings),
            'total_revenue': total_revenue,
        })
