from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if not self.allowed_roles:
            return True
        return getattr(user, 'user_type', None) in self.allowed_roles


class IsSuperAdmin(RolePermission):
    allowed_roles = ('SUPER_ADMIN',)


class IsCompanyStaff(RolePermission):
    allowed_roles = ('COMPANY_STAFF', 'SUPER_ADMIN')


class IsPassenger(RolePermission):
    allowed_roles = ('PASSENGER', 'SUPER_ADMIN')


HasRole = RolePermission
