from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.urls import resolve
from django.contrib.auth import get_user_model

User = get_user_model()


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant data isolation
    """
    
    def process_request(self, request):
        """
        Add tenant context to request based on authenticated user
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Set tenant context based on user type
            if request.user.is_company_staff():
                request.tenant_company = request.user.company
            else:
                request.tenant_company = None
        else:
            request.tenant_company = None
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Enforce tenant-based access control for company dashboard URLs
        """
        current_url = resolve(request.path_info)

        # Prefer URL namespaces over substring checks on names
        namespace = getattr(current_url, 'namespace', None)

        # Super admin area guarded by namespace 'super_admin' (accounts.admin_urls)
        if namespace == 'super_admin' or request.path_info.startswith('/admin/'):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            # Accept either Django superuser flag or custom SUPER_ADMIN type
            if not (getattr(request.user, 'is_superuser', False) or request.user.is_super_admin()):
                return HttpResponseForbidden("Super admin access required")
            return None

        # Company dashboard guarded by namespace 'companies' or path prefix '/company/'
        if namespace == 'companies' or request.path_info.startswith('/company/'):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            if not request.user.is_company_staff():
                return HttpResponseForbidden("Company staff access required")
            if not request.user.company:
                return HttpResponseForbidden("User not assigned to any company")

        return None


class SecurityMiddleware(MiddlewareMixin):
    """
    Additional security middleware for the platform
    """
    
    def process_request(self, request):
        """
        Add security headers and track user sessions
        """
        # Track user sessions for security
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._update_user_session(request)
        
        return None
    
    def _update_user_session(self, request):
        """
        Update or create user session tracking
        """
        from .models import UserSession
        import uuid
        
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Get or create session record
        session, created = UserSession.objects.get_or_create(
            user=request.user,
            session_key=session_key,
            defaults={
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'device_type': self._detect_device_type(request),
            }
        )
        
        if not created:
            session.last_activity = timezone.now()
            session.save(update_fields=['last_activity'])
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _detect_device_type(self, request):
        """
        Detect device type from user agent
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'MOBILE'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'TABLET'
        else:
            return 'WEB'
