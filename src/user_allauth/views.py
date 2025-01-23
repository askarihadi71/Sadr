from typing import Any, Dict
from django import http
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth import get_user_model, logout,login
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordResetDoneView,
)
from django.views import View  
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from allauth.account.views import (
    SignupView,
    ConfirmEmailView,
    EmailView,
    LoginView as allauthhLoginView,
    LogoutView as allauthLogoutView,
    PasswordChangeView as allauthPasswordChangeView,
    PasswordResetView as allauthPasswordResetView,
    PasswordResetFromKeyView as allauthPasswordResetFromKeyView,
    PasswordSetView as allauthPasswordSetView,
    )

from user.senders import send_otp
from .models import OTP, User
from .forms import OTPForm, RegistrationForm,CustomSignupForm, UsernameForm
from user.mixins import VerifiedEmailRequiredMixin
import logging

logger = logging.getLogger('db')


class CustomSignupView(SignupView):
    template_name = 'user/register.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('account_email_verification_sent')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class EmailConfirmView(ConfirmEmailView):
    template_name = "user/email_confirm.html"


class EmailVerificationSentView(TemplateView):
    template_name = "user/verification_sent.html"


class EmailView(EmailView):
    template_name = "user/email_chahnge.html"


class InactiveAccountView(TemplateView):
    template_name = "user/account_inactive.html"


class Login(allauthhLoginView):
    template_name = "user/login.html"


class PassChange(LoginRequiredMixin,VerifiedEmailRequiredMixin, allauthPasswordChangeView):
    template_name = "user/password_change.html"
    success_url = reverse_lazy("user:password_change_done")
     

class PassChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "user/passChangeDone.html"


class PassResetView(allauthPasswordResetView):
     template_name = "user/password_reset.html"
     email_template_name = "user/password_reset_email_template.html"
     success_url = reverse_lazy("user:account_reset_password_done")


class PasswordSetView(allauthPasswordSetView):
    template_name = "user/password_set.html"
    success_url =reverse_lazy("traceapp:main_template_view")


class PassResetDone(PasswordResetDoneView):
     template_name = "user/password_reset_done.html"


class PassResetKeyDone(PasswordResetDoneView):
     template_name = "user/password_reset_key_done.html"


class PassResetConfirm(allauthPasswordResetFromKeyView):
    template_name = "user/password_reset_confirm.html"


class UserRegistrationView(CreateView):
    model = User
    form_class = RegistrationForm
    success_url = reverse_lazy('user:login')
    template_name = "user/register.html"

    def get_context_data(self, **kwargs: reverse_lazy):
        context = super().get_context_data(**kwargs)
        context["tz_choices"] = User.TIMEZONE_CHOICES
        return context
    
    
class UsernameLoginView(View):  
    template_name = "user/login.html"
    
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            return redirect('user:profile')

        form = UsernameForm()  
        return render(request, self.template_name, {'form': form})  
    
    def post(self, request, *args, **kwargs):
        try:
            form = UsernameForm(request.POST)  
            if form.is_valid():  
                username = form.cleaned_data['username']  
                user = User.objects.filter(phone=username).first()  
                if user:  
                    user_otp, created = OTP.objects.get_or_create(user=user)  
                    send_otp(user_otp)  
                    # send_otp_email(user_otp)
                    # send_otp_email.delay(user.pk) 
                    request.session['otp_token'] = str(user_otp.token)  
                return redirect('user:otp_login')  
            return render(request, self.template_name, {'form': form})  
        except Exception as e:
            logger.error(f'login error e: {e}')
            return redirect('user:otp_login')  
        

class OTPLoginView(View):  
    template_name = 'user/login_otp_code.html'  
    
    def get(self, request, *args, **kwargs):  
        form = OTPForm()  
        return render(request, self.template_name, {'form': form})  
    
    def post(self, request, *args, **kwargs):  
        form = OTPForm(request.POST)  
        if form.is_valid():  
            otp_code = form.cleaned_data['otp_code']  
            token = request.session.get('otp_token')  
            user_otp = OTP.objects.filter(token=token).first()  
           
            if user_otp and user_otp.verify_otp(otp_code, True):  
                login(request, user_otp.user)  
                return redirect('user:profile')  
            else:  
                form.add_error(None, 'کد وارد شده صحیح نیست یا منقضی شده است.')  
        return render(request, self.template_name, {'form': form}) 
    

class Profile(LoginRequiredMixin, DetailView):  
    model = User  
    template_name = 'user/profile.html'  
    context_object_name = 'profile'  

    def get_object(self):  
        # Override to get the profile of the logged-in user  
        return self.request.user  