from rest_framework.permissions import BasePermission
from .constants import Role

class UserRolePermission(BasePermission):
    
    allowed_roles = None

    def has_permission(self, request, view):
        
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        roles = self.allowed_roles or getattr(view, 'allowed_roles', [])

        return user.role in roles
    

class IsProvider(UserRolePermission):
    allowed_roles = [Role.NURSE, Role.HEAD_NURSE]

class IsAdmin(UserRolePermission):
    allowed_roles = [Role.ADMIN]

class IsPatient(UserRolePermission):
    allowed_roles = [Role.PATIENT]

class IsCaregiver(UserRolePermission):
    allowed_roles = [Role.CAREGIVER]


