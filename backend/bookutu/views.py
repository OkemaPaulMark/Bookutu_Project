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

@api_view(['GET'])
@permission_classes([AllowAny])
def adverts_list(request):
    """
    GET: List active adverts
    Optional query param: ?all=true to fetch all active adverts ignoring dates
    """
    today = timezone.now().date()
    fetch_all = request.GET.get('all', 'false').lower() == 'true'

    if fetch_all:
        # Fetch all active adverts ignoring start/end dates
        adverts = Advert.objects.filter(is_active=True)
    else:
        # Fetch only adverts within schedule
        adverts = Advert.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__lte=today) | Q(start_date__isnull=True),
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        )

    serializer = AdvertSerializer(adverts, many=True, context={'request': request})
    data = serializer.data
    
    # Add Google URLs for testing
    google_urls = [
        'https://www.google.com',
        'https://www.google.com/search?q=bus+booking',
        'https://www.google.com/maps',
        'https://www.google.com/search?q=travel'
    ]
    
    for i, advert in enumerate(data):
        if i < len(google_urls):
            advert['link_url'] = google_urls[i]
        else:
            advert['link_url'] = 'https://www.google.com'
    
    return Response(data)