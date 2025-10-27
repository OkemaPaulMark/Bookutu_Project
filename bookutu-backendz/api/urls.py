from django.urls import path
from .views import public_trips, add_trip 

urlpatterns = [
    path('trips/', public_trips, name='public-trips'),
    path('trips/add/', add_trip, name='add-trip'),
]



