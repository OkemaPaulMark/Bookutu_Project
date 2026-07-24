from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Bus, BusSeat, Driver, Route
from .serializers import BusSerializer, DriverSerializer, RouteSerializer

SEAT_POSITIONS = ['LEFT_WINDOW', 'LEFT_AISLE', 'RIGHT_AISLE', 'RIGHT_WINDOW']
SEAT_LETTERS = ['A', 'B', 'C', 'D']


def _create_seats(bus, total_seats):
    seat_count = (total_seats // 4) * 4
    rows = seat_count // 4
    if rows <= 0:
        return

    seats = []
    for row_index in range(rows):
        row_number = row_index + 1
        for i, letter in enumerate(SEAT_LETTERS):
            seats.append(BusSeat(
                bus=bus,
                seat_number=f'{row_number}{letter}',
                row_number=row_number,
                seat_position=SEAT_POSITIONS[i],
                seat_type='REGULAR',
                is_window=i in (0, 3),
                is_aisle=i in (1, 2),
                has_extra_legroom=False,
                price_multiplier=1,
            ))
    BusSeat.objects.bulk_create(seats)


def _scoped_queryset(queryset, user):
    if user.user_type == 'SUPER_ADMIN':
        return queryset
    if user.user_type == 'COMPANY_STAFF' and user.company_id:
        return queryset.filter(company_id=user.company_id)
    return queryset.none()


def _check_object_access(user, obj):
    return user.user_type == 'SUPER_ADMIN' or user.company_id == obj.company_id


def _resolve_company_id(request):
    """Returns (company_id, error_response). Staff are forced to their own company; super admins must supply one; anyone else is rejected."""
    if request.user.user_type == 'COMPANY_STAFF':
        return request.user.company_id, None
    if request.user.user_type != 'SUPER_ADMIN':
        return None, Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
    company_id = request.data.get('company_id')
    if not company_id:
        return None, Response({'detail': 'companyId is required.'}, status=status.HTTP_400_BAD_REQUEST)
    return company_id, None


def _update_payload(request):
    """Strips company_id from update payloads for non-super-admins, so staff can't reassign records to another company."""
    if request.user.user_type == 'SUPER_ADMIN':
        return request.data
    return {key: value for key, value in request.data.items() if key != 'company_id'}


class BusViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = _scoped_queryset(Bus.objects.all(), request.user)
        serializer = BusSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if not _check_object_access(request.user, bus):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': BusSerializer(bus).data})

    def create(self, request):
        company_id, error = _resolve_company_id(request)
        if error:
            return error

        data = dict(request.data)
        data['company_id'] = company_id
        serializer = BusSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        bus = serializer.save()
        _create_seats(bus, bus.total_seats)
        return Response({'data': BusSerializer(bus).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        bus = get_object_or_404(Bus, pk=pk)
        if not _check_object_access(request.user, bus):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BusSerializer(bus, data=_update_payload(request), partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})


class RouteViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = _scoped_queryset(Route.objects.all(), request.user)
        serializer = RouteSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        route = get_object_or_404(Route, pk=pk)
        if not _check_object_access(request.user, route):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': RouteSerializer(route).data})

    def create(self, request):
        company_id, error = _resolve_company_id(request)
        if error:
            return error

        data = dict(request.data)
        data['company_id'] = company_id
        serializer = RouteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        route = serializer.save()
        return Response({'data': RouteSerializer(route).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        route = get_object_or_404(Route, pk=pk)
        if not _check_object_access(request.user, route):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RouteSerializer(route, data=_update_payload(request), partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})


class DriverViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = _scoped_queryset(Driver.objects.all(), request.user)
        serializer = DriverSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        driver = get_object_or_404(Driver, pk=pk)
        if not _check_object_access(request.user, driver):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': DriverSerializer(driver).data})

    def create(self, request):
        company_id, error = _resolve_company_id(request)
        if error:
            return error

        data = dict(request.data)
        data['company_id'] = company_id
        serializer = DriverSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()
        return Response({'data': DriverSerializer(driver).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        driver = get_object_or_404(Driver, pk=pk)
        if not _check_object_access(request.user, driver):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = DriverSerializer(driver, data=_update_payload(request), partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})
