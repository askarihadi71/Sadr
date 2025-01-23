from rest_framework.permissions import BasePermission
from allauth.account.models import EmailAddress 


class VerifiedEmailRequiredPermission(BasePermission):
    def has_permission(self, request, view):
        if not EmailAddress.objects.filter(user=request.user, verified=True).exists():
            return False
        else:
            return True


class MLMachinePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_ml:
            return False
        else:
            return True


class SuperUserPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser:
            return False
        else:
            return True
    
        
class SuperUserOr_ML_Permission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_ml:
            return True
        else:
            return False


class SupportOperatorOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_support_operator or request.user.is_superuser:
            return True
        else:
            return False
        