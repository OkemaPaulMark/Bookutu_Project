from django.urls import path
from . import admin_views

app_name = 'super_admin'

urlpatterns = [
    # Dashboard
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Companies Management
    path('companies/', admin_views.admin_companies, name='admin_companies'),
    path('companies/create/', admin_views.create_company, name='create_company'),
    path('companies/<int:company_id>/', admin_views.company_detail, name='company_detail'),
    path('companies/<int:company_id>/edit/', admin_views.edit_company, name='edit_company'),
    path('companies/<int:company_id>/toggle-status/', admin_views.toggle_company_status, name='toggle_company_status'),
    path('companies/<int:company_id>/toggle-verification/', admin_views.toggle_company_verification, name='toggle_company_verification'),
    
    # Bookings Management
    path('bookings/', admin_views.admin_bookings, name='admin_bookings'),
    path('bookings/<int:booking_id>/', admin_views.booking_detail, name='booking_detail'),
    
    # Financial Reports
    path('financials/', admin_views.admin_financials, name='admin_financials'),
    
    # System Management
    path('settings/', admin_views.admin_settings, name='admin_settings'),
    path('logs/', admin_views.admin_logs, name='admin_logs'),
    path('create-superuser/', admin_views.create_superuser, name='create_superuser'),

    # Adverts Management
    path('adverts/', admin_views.admin_adverts, name='admin_adverts'),
    path('adverts/create/', admin_views.create_advert, name='create_advert'),
    path('adverts/<int:advert_id>/edit/', admin_views.edit_advert, name='edit_advert'),
    path('adverts/<int:advert_id>/toggle-status/', admin_views.toggle_advert_status, name='toggle_advert_status'),
    path('adverts/<int:advert_id>/delete/', admin_views.delete_advert, name='delete_advert'),
]