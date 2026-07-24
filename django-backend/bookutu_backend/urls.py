from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'bookutu-django-backend'})


urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]
