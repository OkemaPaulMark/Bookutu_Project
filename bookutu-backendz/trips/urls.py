from django.urls import path
from .views import (
    RouteListCreateView, RouteDetailView, TripListCreateView, TripDetailView,
    TripManifestView, trip_dashboard_stats
)

urlpatterns = [
    # Route Management
    path('routes/', RouteListCreateView.as_view(), name='company_routes'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='company_route_detail'),
    
    # Trip Management
    path('', TripListCreateView.as_view(), name='company_trips'),
    path('<int:pk>/', TripDetailView.as_view(), name='company_trip_detail'),
    path('<int:trip_id>/manifest/', TripManifestView.as_view(), name='trip_manifest'),
    
    # Dashboard
    path('dashboard/stats/', trip_dashboard_stats, name='trip_dashboard_stats'),
]
