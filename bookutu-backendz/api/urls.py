from django.urls import path
from .views import (
    public_trips, add_trip, MobileRegisterView, MobileLoginView, MobileLogoutView
)

urlpatterns = [
    # Authentication endpoints for mobile app
    path('register/', MobileRegisterView.as_view(), name='mobile-register'),
    path('login/', MobileLoginView.as_view(), name='mobile-login'),
    path('logout/', MobileLogoutView.as_view(), name='mobile-logout'),

    # Trip endpoints
    path('trips/', public_trips, name='public-trips'),
    path('trips/add/', add_trip, name='add-trip'),
]



