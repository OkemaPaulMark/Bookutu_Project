from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q

from .models import Advert
from .serializers import AdvertSerializer


def home_view(request):
    """Redirect to login page"""
    return redirect('/accounts/login/')


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'bookutu-backend'})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # 👈 allow public access
def adverts_list(request):
    """
    GET: List active adverts
    POST: Create a new advert
    """
    if request.method == 'GET':
        today = timezone.now().date()
        adverts = Advert.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__lte=today) | Q(start_date__isnull=True),
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        )
        serializer = AdvertSerializer(adverts, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdvertSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
