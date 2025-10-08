from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompatCompanyViewSet,
    CompatBusViewSet,
    CompatRouteViewSet,
    CompatTripViewSet,
    CompatBookingViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompatCompanyViewSet, basename='compat-company')
router.register(r'buses', CompatBusViewSet, basename='compat-bus')
router.register(r'routes', CompatRouteViewSet, basename='compat-route')
router.register(r'trips', CompatTripViewSet, basename='compat-trip')
router.register(r'bookings', CompatBookingViewSet, basename='compat-booking')

urlpatterns = [
    path('', include(router.urls)),
]


