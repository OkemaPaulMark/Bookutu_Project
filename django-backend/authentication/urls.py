from rest_framework.routers import DefaultRouter

from .views import AuthViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'auth', AuthViewSet, basename='auth')
