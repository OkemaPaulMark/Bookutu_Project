from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Dashboard
    path('', views.company_dashboard, name='dashboard'),
    path('dashboard/', views.company_dashboard, name='dashboard'),
    
    # Bookings
    path('bookings/', views.company_bookings, name='bookings'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    
    # Fleet Management
    path('fleet/', views.company_fleet, name='fleet'),
    path('fleet/create/', views.create_bus, name='create_bus'),
    path('fleet/<int:bus_id>/', views.bus_detail, name='bus_detail'),
    path('fleet/<int:bus_id>/edit/', views.edit_bus, name='edit_bus'),
    
    # Routes
    path('routes/', views.company_routes, name='routes'),
    path('routes/create/', views.create_route, name='create_route'),
    path('routes/<int:route_id>/', views.route_detail, name='route_detail'),
    path('routes/<int:route_id>/edit/', views.edit_route, name='edit_route'),
    
    # Drivers
    path('drivers/', views.company_drivers, name='drivers'),
    path('drivers/create/', views.create_driver, name='create_driver'),
    path('drivers/<int:driver_id>/', views.driver_detail, name='driver_detail'),
    path('drivers/<int:driver_id>/edit/', views.edit_driver, name='edit_driver'),
    
    # Reports and Settings
    path('reports/', views.company_reports, name='reports'),
    path('settings/', views.company_settings, name='settings'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.create_staff, name='create_staff'),

    # Trips
    path('trips/', views.company_trips, name='trips'),
    path('trips/create/', views.create_trip, name='create_trip'),
    path('trips/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:trip_id>/edit/', views.edit_trip, name='edit_trip'),
    path('trips/<int:trip_id>/manifest/', views.trip_manifest, name='trip_manifest'),
]