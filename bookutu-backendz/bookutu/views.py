from django.shortcuts import render, redirect
from django.http import JsonResponse


def home_view(request):
    """Redirect to login page"""
    return redirect('/accounts/login/')


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'bookutu-backend'})