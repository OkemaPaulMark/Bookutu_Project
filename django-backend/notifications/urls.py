from rest_framework.routers import DefaultRouter

from .views import AnnouncementViewSet, SystemLogViewSet

router = DefaultRouter()
router.register(r'notifications', AnnouncementViewSet, basename='notifications')
router.register(r'notifications/logs', SystemLogViewSet, basename='notification-logs')
