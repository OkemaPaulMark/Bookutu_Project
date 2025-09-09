from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    hello_world,
    FeedbackListCreateView,
    RegisterView, LoginView,
    BusCompanyViewSet, BusViewSet, RouteViewSet, TripViewSet, SeatViewSet, BookingViewSet, PaymentViewSet, SeatBookingViewSet,
)

router = DefaultRouter()
router.register(r'companies', BusCompanyViewSet)
router.register(r'buses', BusViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'trips', TripViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'seat-bookings', SeatBookingViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('hello/', hello_world, name='hello_world'),
    path('feedback/', FeedbackListCreateView.as_view(), name='feedback'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
