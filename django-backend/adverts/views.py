from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from common.permissions import IsCompanyStaff

from .models import Advert
from .serializers import AdvertSerializer


class AdvertViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsCompanyStaff()]
        return super().get_permissions()

    def list(self, request):
        queryset = Advert.objects.all()
        if request.user.user_type not in ('SUPER_ADMIN', 'COMPANY_STAFF'):
            queryset = queryset.filter(is_active=True)
        serializer = AdvertSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        advert = get_object_or_404(Advert, pk=pk)
        return Response({'data': AdvertSerializer(advert).data})

    def create(self, request):
        serializer = AdvertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        advert = serializer.save()
        return Response({'data': AdvertSerializer(advert).data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        advert = get_object_or_404(Advert, pk=pk)
        serializer = AdvertSerializer(advert, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    def destroy(self, request, pk=None):
        advert = get_object_or_404(Advert, pk=pk)
        advert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
