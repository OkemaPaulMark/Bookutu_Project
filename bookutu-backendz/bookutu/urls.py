from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # Root and health check
    path("", views.home_view, name="home"),
    path("health/", views.health_check, name="health_check"),
    # Django admin
    path("django-admin/", admin.site.urls),
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Web Authentication (session-based)
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    # Core API v1 endpoints
    path('api/v1/auth/', include(('accounts.urls', 'accounts'), namespace='api_accounts')),
    path('api/v1/companies/', include(('companies.urls', 'companies'), namespace='companies')),
    path('api/v1/trips/', include(('trips.urls', 'trips'), namespace='trips')),
    path('api/v1/bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    path('api/v1/payments/', include(('payments.urls', 'payments'), namespace='payments')),

    # Group compatibility endpoints
    path('api/group-compat/', include(('group_compat.urls', 'group_compat'), namespace='group_compat')),

    # Dashboards
    path('company/', include('companies.urls')),
    path('admin/', include('accounts.admin_urls')),

    # Adverts
    path('api/adverts/', views.adverts_list, name='api_adverts'),

    # ✅ Mobile API for Flutter app
    path('api/auth/', include('api.urls')),
]

# Serve static & media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
