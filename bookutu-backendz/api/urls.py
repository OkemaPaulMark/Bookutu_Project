from django.urls import path
from .views import (
    public_trips, add_trip, MobileRegisterView, MobileLoginView, MobileLogoutView,
    get_trip_seats, create_booking
) 

urlpatterns = [
    # Authentication endpoints for mobile app
    path('register/', MobileRegisterView.as_view(), name='mobile-register'),
    path('login/', MobileLoginView.as_view(), name='mobile-login'),
    path('logout/', MobileLogoutView.as_view(), name='mobile-logout'),
    
    path('trips/', public_trips, name='public-trips'),
    path('trips/add/', add_trip, name='add-trip'),
    path('trips/<int:trip_id>/seats/', get_trip_seats, name='trip-seats'),
    path('bookings/create/', create_booking, name='create-booking'),
]