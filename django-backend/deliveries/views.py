import random
import string

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Delivery
from .serializers import DeliverySerializer


def _generate_tracking_number():
    while True:
        digits = ''.join(random.choices(string.digits, k=4))
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        tracking_number = f'DEL{digits}{letters}'
        if not Delivery.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number


def _scoped_queryset(queryset, user):
    if user.user_type == 'SUPER_ADMIN':
        return queryset
    if user.user_type == 'COMPANY_STAFF' and user.company_id:
        return queryset.filter(company_id=user.company_id)
    return queryset.none()


def _check_object_access(user, delivery):
    return user.user_type == 'SUPER_ADMIN' or user.company_id == delivery.company_id


def _resolve_company_id(request):
    """Staff are forced to their own company; super admins must supply one; anyone else is rejected."""
    if request.user.user_type == 'COMPANY_STAFF':
        return request.user.company_id, None
    if request.user.user_type != 'SUPER_ADMIN':
        return None, Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
    company_id = request.data.get('company_id')
    if not company_id:
        return None, Response({'detail': 'companyId is required.'}, status=status.HTTP_400_BAD_REQUEST)
    return company_id, None


class DeliveryViewSet(viewsets.ViewSet):

    def _base_queryset(self):
        return Delivery.objects.select_related('registered_by', 'picked_up_by')

    def list(self, request):
        queryset = _scoped_queryset(self._base_queryset(), request.user)

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(tracking_number__icontains=search)
                | Q(sender_name__icontains=search)
                | Q(sender_phone__icontains=search)
                | Q(receiver_name__icontains=search)
                | Q(receiver_phone__icontains=search)
            )

        serializer = DeliverySerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        delivery = get_object_or_404(self._base_queryset(), pk=pk)
        if not _check_object_access(request.user, delivery):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': DeliverySerializer(delivery).data})

    def create(self, request):
        if request.user.user_type not in ('SUPER_ADMIN', 'COMPANY_STAFF'):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        company_id, error = _resolve_company_id(request)
        if error:
            return error

        data = dict(request.data)
        data['company_id'] = company_id
        serializer = DeliverySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        delivery = serializer.save(
            tracking_number=_generate_tracking_number(),
            registered_by=request.user,
        )
        return Response({'data': DeliverySerializer(delivery).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        delivery = get_object_or_404(Delivery, pk=pk)
        if not _check_object_access(request.user, delivery):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        data = {key: value for key, value in request.data.items() if key != 'company_id'}
        serializer = DeliverySerializer(delivery, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    ALLOWED_STATUS_TRANSITIONS = {
        'REGISTERED': {'ON_DELIVERY', 'PICKED_UP', 'CANCELLED'},
        'ON_DELIVERY': {'PICKED_UP', 'CANCELLED'},
        'PICKED_UP': set(),
        'CANCELLED': set(),
    }

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        delivery = get_object_or_404(Delivery, pk=pk)
        if not _check_object_access(request.user, delivery):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        if new_status not in dict(self.ALLOWED_STATUS_TRANSITIONS):
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in self.ALLOWED_STATUS_TRANSITIONS[delivery.status]:
            return Response(
                {'detail': f'Cannot change status from {delivery.status} to {new_status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.status = new_status
        update_fields = ['status', 'updated_at']
        if new_status == 'PICKED_UP':
            delivery.picked_up_by = request.user
            delivery.picked_up_at = timezone.now()
            update_fields += ['picked_up_by', 'picked_up_at']
        delivery.save(update_fields=update_fields)
        return Response({'data': DeliverySerializer(delivery).data})

    def destroy(self, request, pk=None):
        delivery = get_object_or_404(Delivery, pk=pk)
        if not _check_object_access(request.user, delivery):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        delivery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
