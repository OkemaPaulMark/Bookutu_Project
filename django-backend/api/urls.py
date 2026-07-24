from django.urls import include, path

from authentication.urls import router as auth_router
from companies.urls import router as companies_router
from fleet.urls import router as fleet_router
from trips.urls import router as trips_router
from bookings.urls import router as bookings_router
from payments.urls import router as payments_router
from notifications.urls import router as notifications_router
from adverts.urls import router as adverts_router
from deliveries.urls import router as deliveries_router

urlpatterns = [
    path('', include(auth_router.urls)),
    path('', include(companies_router.urls)),
    path('', include(fleet_router.urls)),
    path('', include(trips_router.urls)),
    path('', include(bookings_router.urls)),
    path('', include(payments_router.urls)),
    path('', include(notifications_router.urls)),
    path('', include(adverts_router.urls)),
    path('', include(deliveries_router.urls)),
]
