from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import path, include, reverse
from django.views.generic.base import RedirectView
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation


class VerifiedEmailRequiredMixin(AccessMixin):
    """
    Mixin to ensure the user has a verified email address.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not EmailAddress.objects.filter(user=request.user, verified=True).exists():
            send_email_confirmation(request, request.user)
            return render(request, "user/verified_email_required.html")
        return super().dispatch(request, *args, **kwargs)