from rest_framework.routers import DefaultRouter

from .views import DeliveryViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'deliveries', DeliveryViewSet, basename='deliveries')
