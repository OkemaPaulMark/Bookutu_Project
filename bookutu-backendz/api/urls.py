from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import mobile_views

app_name = 'mobile_api'

urlpatterns = [
    # Authentication
    path('auth/login/', mobile_views.MobileTokenObtainPairView.as_view(), name='mobile_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', mobile_views.mobile_register, name='mobile_register'),
    
    # Trip Search & Booking
    path('trips/search/', mobile_views.search_trips, name='search_trips'),
    path('trips/<int:trip_id>/', mobile_views.trip_details, name='trip_details'),
    path('routes/popular/', mobile_views.popular_routes, name='popular_routes'),
    
    # Bookings
    path('bookings/', mobile_views.MobileBookingListView.as_view(), name='booking_list'),
    path('bookings/create/', mobile_views.MobileBookingCreateView.as_view(), name='create_booking'),
    path('bookings/<int:booking_id>/', mobile_views.booking_details, name='booking_details'),
    path('bookings/<int:booking_id>/cancel/', mobile_views.cancel_booking, name='cancel_booking'),
    
    # User Profile
    path('profile/', mobile_views.user_profile, name='user_profile'),
    path('profile/update/', mobile_views.update_profile, name='update_profile'),
    
    # Device Management
    path('devices/register/', mobile_views.register_device, name='register_device'),
]
