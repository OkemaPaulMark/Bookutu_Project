from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Announcement, SystemLog
from .serializers import AnnouncementSerializer, SystemLogSerializer


class AnnouncementViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Announcement.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AnnouncementSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SystemLogViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = SystemLog.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = SystemLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
