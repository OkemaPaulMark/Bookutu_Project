from django.urls import path
from .direct_booking_views import (
    DirectBookingRoutesView, DirectBookingTripsView, DirectBookingSeatsView,
    SeatReservationView, DirectBookingCreateView, print_ticket,
    resend_sms_ticket, direct_booking_stats
)
from .views import (
    BookingListView, BookingDetailView, BookingCancelView,
    BookingHistoryView, company_booking_manifest
)

urlpatterns = [
    # Regular booking management
    path('', BookingListView.as_view(), name='company_bookings'),
    path('<int:pk>/', BookingDetailView.as_view(), name='company_booking_detail'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='company_booking_cancel'),
    path('<int:pk>/history/', BookingHistoryView.as_view(), name='company_booking_history'),
    path('manifest/', company_booking_manifest, name='company_booking_manifest'),
    
    # Direct booking system
    path('direct/routes/', DirectBookingRoutesView.as_view(), name='direct_booking_routes'),
    path('direct/trips/', DirectBookingTripsView.as_view(), name='direct_booking_trips'),
    path('direct/trips/<int:trip_id>/seats/', DirectBookingSeatsView.as_view(), name='direct_booking_seats'),
    path('direct/reserve-seat/', SeatReservationView.as_view(), name='direct_booking_reserve_seat'),
    path('direct/create/', DirectBookingCreateView.as_view(), name='direct_booking_create'),
    path('direct/stats/', direct_booking_stats, name='direct_booking_stats'),
    
    # Ticket management
    path('<int:booking_id>/print-ticket/', print_ticket, name='print_ticket'),
    path('<int:booking_id>/resend-sms/', resend_sms_ticket, name='resend_sms_ticket'),
]
