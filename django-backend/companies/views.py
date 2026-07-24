import re

from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.models import Booking
from common.permissions import IsSuperAdmin
from fleet.models import Bus
from trips.models import Trip

from .models import Company
from .serializers import STAFF_EDITABLE_COMPANY_FIELDS, CompanySerializer


def _to_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9\s-]', '', value)
    value = re.sub(r'\s+', '-', value)
    value = re.sub(r'-+', '-', value)
    return value


def _generate_unique_slug(name: str) -> str:
    base = _to_slug(name) or 'company'
    slug = base
    suffix = 1
    while Company.objects.filter(slug=slug).exists():
        suffix += 1
        slug = f'{base}-{suffix}'
    return slug


class CompanyViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in {'create', 'destroy', 'platform_stats'}:
            return [IsSuperAdmin()]
        return super().get_permissions()

    def list(self, request):
        user = request.user

        if user.user_type == 'SUPER_ADMIN':
            queryset = Company.objects.all()
            status_filter = request.query_params.get('status')
            search = request.query_params.get('search')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search)
                )
            serializer = CompanySerializer(queryset, many=True)
            return Response({'data': serializer.data})

        if user.user_type == 'COMPANY_STAFF' and user.company_id:
            queryset = Company.objects.filter(id=user.company_id)
            serializer = CompanySerializer(queryset, many=True)
            return Response({'data': serializer.data})

        return Response({'data': []})

    def retrieve(self, request, pk=None):
        company = get_object_or_404(Company, pk=pk)
        user = request.user
        if user.user_type != 'SUPER_ADMIN' and user.company_id != company.id:
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': CompanySerializer(company).data})

    def create(self, request):
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slug = _generate_unique_slug(serializer.validated_data['name'])
        company = serializer.save(slug=slug)
        return Response({'data': CompanySerializer(company).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        company = get_object_or_404(Company, pk=pk)
        user = request.user

        if user.user_type != 'SUPER_ADMIN' and user.company_id != company.id:
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if user.user_type != 'SUPER_ADMIN':
            data = {key: value for key, value in request.data.items() if key in STAFF_EDITABLE_COMPANY_FIELDS}

        serializer = CompanySerializer(company, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    def destroy(self, request, pk=None):
        company = get_object_or_404(Company, pk=pk)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='platform/stats')
    def platform_stats(self, request):
        status_counts = dict(
            Company.objects.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        confirmed_or_completed = ['CONFIRMED', 'COMPLETED']
        total_revenue = Booking.objects.filter(status__in=confirmed_or_completed).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        recent_companies = Company.objects.order_by('-created_at')[:5]

        top_companies = (
            Company.objects.annotate(
                booking_count=Count('bookings', distinct=True),
                trip_count=Count('trips', distinct=True),
                bus_count=Count('buses', distinct=True),
            )
            .order_by('-booking_count')[:5]
        )

        six_months_ago = (timezone.now() - timezone.timedelta(days=180)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        recent_bookings = Booking.objects.filter(
            status__in=confirmed_or_completed,
            created_at__gte=six_months_ago,
        ).values('created_at', 'total_amount')

        monthly_map = {}
        for booking in recent_bookings:
            key = booking['created_at'].strftime('%Y-%m')
            monthly_map[key] = monthly_map.get(key, 0) + float(booking['total_amount'])
        monthly_revenue = [
            {'month': month, 'revenue': revenue}
            for month, revenue in sorted(monthly_map.items())
        ]

        return Response({'data': {
            'companies': {
                'total': sum(status_counts.values()),
                'active': status_counts.get('ACTIVE', 0),
                'pending': status_counts.get('PENDING', 0),
                'suspended': status_counts.get('SUSPENDED', 0),
                'inactive': status_counts.get('INACTIVE', 0),
            },
            'total_trips': Trip.objects.count(),
            'total_bookings': Booking.objects.count(),
            'total_revenue': float(total_revenue),
            'monthly_revenue': monthly_revenue,
            'recent_companies': [
                {
                    'id': c.id, 'name': c.name, 'city': c.city,
                    'status': c.status, 'created_at': c.created_at,
                }
                for c in recent_companies
            ],
            'top_companies': [
                {
                    'id': c.id, 'name': c.name, 'city': c.city, 'status': c.status,
                    'bookings': c.booking_count, 'trips': c.trip_count, 'buses': c.bus_count,
                }
                for c in top_companies
            ],
        }})
