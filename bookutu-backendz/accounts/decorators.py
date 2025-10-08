from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def user_type_required(user_types):
    """
    Decorator to require specific user types
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type not in user_types:
                return HttpResponseForbidden("Access denied")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def company_staff_required(view_func):
    """
    Decorator to require company staff access
    """
    return user_type_required(['COMPANY_STAFF'])(view_func)


def super_admin_required(view_func):
    """
    Decorator to require super admin access
    """
    return user_type_required(['SUPER_ADMIN'])(view_func)


def passenger_required(view_func):
    """
    Decorator to require passenger access
    """
    return user_type_required(['PASSENGER'])(view_func)


def verified_user_required(view_func):
    """
    Decorator to require verified user
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_verified:
            return HttpResponseForbidden("Email verification required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def same_company_required(view_func):
    """
    Decorator to ensure company staff can only access their company's data
    """
    @wraps(view_func)
    @company_staff_required
    def _wrapped_view(request, *args, **kwargs):
        # This decorator works with views that have company_id in URL
        company_id = kwargs.get('company_id')
        if company_id and str(request.user.company.id) != str(company_id):
            return HttpResponseForbidden("Access denied to other company's data")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
