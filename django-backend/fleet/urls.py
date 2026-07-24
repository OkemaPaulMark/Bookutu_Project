from rest_framework.routers import DefaultRouter

from .views import BusViewSet, DriverViewSet, RouteViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'fleet/buses', BusViewSet, basename='fleet-buses')
router.register(r'fleet/routes', RouteViewSet, basename='fleet-routes')
router.register(r'fleet/drivers', DriverViewSet, basename='fleet-drivers')
