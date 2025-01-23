from rest_framework.permissions import BasePermission
from nazer.models import Device

class DeviceDataPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
       

    def has_object_permission(self, request, view, obj: Device):
        return bool(request.user.is_superuser or obj.user == request.user)