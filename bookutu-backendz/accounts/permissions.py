from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user





class IsCompanyStaff(BasePermission):
    """
    Permission class for company staff access
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'COMPANY_STAFF' and
            request.user.company is not None
        )


class IsSuperAdmin(BasePermission):
    """
    Permission class for super admin access
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'SUPER_ADMIN'
        )


class IsCompanyStaffOrSuperAdmin(BasePermission):
    """
    Permission class for company staff or super admin access
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['COMPANY_STAFF', 'SUPER_ADMIN']
        )


class IsSameCompany(BasePermission):
    """
    Permission to ensure company staff can only access their company's data
    """
    
    def has_object_permission(self, request, view, obj):
        # Super admins can access everything
        if request.user.user_type == 'SUPER_ADMIN':
            return True
        
        # Company staff can only access their company's data
        if request.user.user_type == 'COMPANY_STAFF':
            # Check if object has a company attribute
            if hasattr(obj, 'company'):
                return obj.company == request.user.company
            # Check if object is a company itself
            elif obj.__class__.__name__ == 'Company':
                return obj == request.user.company
        
        return False


class IsVerifiedUser(BasePermission):
    """
    Permission class for verified users only
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_verified
        )


class CanCreateDirectBooking(BasePermission):
    """
    Permission for creating direct bookings (company staff only)
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'COMPANY_STAFF' and
            request.user.company is not None and
            request.user.company.is_active()
        )
