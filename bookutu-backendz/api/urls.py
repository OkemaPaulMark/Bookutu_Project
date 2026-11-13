from django.urls import path
from .views import (
    public_trips, add_trip, MobileRegisterView, MobileLoginView, MobileLogoutView
)
from . import mobile_views as mv
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints for mobile app
    path('register/', MobileRegisterView.as_view(), name='mobile-register'),
    path('login/', MobileLoginView.as_view(), name='mobile-login'),
    path('logout/', MobileLogoutView.as_view(), name='mobile-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='mobile-token-refresh'),

    # Profile
    path('profile/', mv.my_profile, name='mobile-profile'),
    path('profile/update/', mv.edit_profile, name='mobile-profile-update'),

    # Trip endpoints
    path('trips/', public_trips, name='public-trips'),
    path('trips/add/', add_trip, name='add-trip'),
    path('trips/<int:trip_id>/', mv.trip_details, name='mobile-trip-details'),
    path('popular-routes/', mv.popular_routes, name='mobile-popular-routes'),

    # Bookings & payment
    path('bookings/', mv.MobileBookingListView.as_view(), name='mobile-bookings'),
    path('bookings/create/', mv.create_bookings, name='mobile-bookings-create'),
    path('bookings/pay/', mv.pay_bookings, name='mobile-bookings-pay'),
    path('bookings/<int:booking_id>/', mv.booking_details, name='mobile-booking-detail'),
    path('bookings/<int:booking_id>/cancel/', mv.cancel_booking, name='mobile-booking-cancel'),

    # Map & notifications
    path('map/', mv.map_data, name='mobile-map'),
    path('notifications/', mv.notifications_feed, name='mobile-notifications'),
]
