from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, CompanyStaffRegistrationView,
    UserProfileView, PasswordChangeView, PasswordResetRequestView,
    PasswordResetConfirmView, UserSessionsView, LogoutView, LogoutAllView,
    verify_email, user_dashboard_data, web_login, web_logout, DashboardRedirectView,
    web_password_reset, company_register, MobileRegisterView, MobileLoginView
)

urlpatterns = [
    # Web Authentication (session-based) - must come first
    path('login/', web_login, name='login'),
    path('register/company/', company_register, name='company_register'),

    path('logout/', web_logout, name='web_logout'),
    path('password-reset/', web_password_reset, name='password_reset'),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard_redirect'),

    # API Authentication
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/logout-all/', LogoutAllView.as_view(), name='logout_all'),

    # Registration
    path('api/register/staff/', CompanyStaffRegistrationView.as_view(), name='staff_register'),

    # Profile Management
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/verify-email/', verify_email, name='verify_email'),

    # Password Management
    path('api/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('api/password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Session Management
    path('api/sessions/', UserSessionsView.as_view(), name='user_sessions'),

    # Dashboard
    path('api/dashboard/', user_dashboard_data, name='user_dashboard'),
    
    
    path('api/mobile/register/', MobileRegisterView.as_view(), name='mobile_register'),
path('api/mobile/login/', MobileLoginView.as_view(), name='mobile_login'),
    
    
]
