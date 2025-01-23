from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin


class SuperuserAccessMixin(LoginRequiredMixin, PermissionRequiredMixin):
    def has_permission(self):
	    return  self.request.user.is_superuser
 
