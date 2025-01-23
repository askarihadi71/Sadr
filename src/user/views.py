import uuid
from django.db.models import Q

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout,login
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.views import View  
from django.contrib import messages
from .models import ChangePhoneOTP, EmailConfirmation, User, OTP
from .mixins import SuperuserAccessMixin
from .forms import ChangeEmailForm, ChangePhoneForm, ChangePhoneRequestForm, UserCreateForm, UsernameForm, OTPForm
from .senders import send_otp, send_phone_change_codes, send_verification_email, send_verification_change_email
import logging

logger = logging.getLogger("db")
sp_logger = logging.getLogger("sp_db")


class UserPassLogin(DjangoLoginView):
    template_name = 'user/userpass_login.html'  
    

class Profile(LoginRequiredMixin, DetailView):
    model = User
    template_name = "user/profile.html"

    def get_object(self):
        # get_all_views(sss.urlpatterns)
        return User.objects.get(pk=self.request.user.pk)

    def get_form_kwargs(self):
        kwarg = super(Profile, self).get_form_kwargs()
        kwarg.update({"user": self.request.user})
        return kwarg


@login_required
def UserLogout(request):
    logout(request)
    return redirect('user:username_login')


class UsersList(SuperuserAccessMixin, ListView):
    template_name = "user/users_list.html"
    paginate_by = 10
    model = User
    ordering = ['pk']

    def get_queryset(self):  
        queryset = super().get_queryset()  
        search_query = self.request.GET.get('search', '') 
        
        if search_query:  
            queryset = queryset.filter(  
                Q(email__icontains=search_query) |  
                Q(first_name__icontains=search_query) |  
                Q(phone__icontains=search_query) |  
                Q(last_name__icontains=search_query)  
            )  
        
        return queryset 


class CreateUser(SuperuserAccessMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "user/user_create_update.html"
    success_url = reverse_lazy("user:users_list")
    
    def form_valid(self, form):
        return super().form_valid(form)


class DeleteUser(SuperuserAccessMixin, DeleteView):
    model = User
    template_name = "user/user-confirm-delete.html"
    success_url = reverse_lazy("user:users_list")


class UserEdit(SuperuserAccessMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = "user/user_create_update.html"
    success_url = reverse_lazy("user:users_list")
    context_object_name = "item"

    def form_valid(self, form):
        return super().form_valid(form)
    
from django.contrib.auth.forms import SetPasswordForm

@login_required()
def set_pass(request, pk):
    if not request.user.is_superuser:
        return redirect("account:profile")
    if request.method == "POST":
        fm = SetPasswordForm(user=User.objects.get(pk=pk), data=request.POST)
        if fm.is_valid():
            fm.save()
            return redirect("user:users_list")
    else:
        user = User.objects.get(pk=pk)
        fm = SetPasswordForm(user=user)
    return render(request, "user/users_pass_reset.html", {"form": fm})


class UsernameLoginView(View):  
    template_name = 'user/otp_login.html'  
    
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
                user = User.objects.filter(Q(phone=username) | Q(phone=username[1:])).first()  
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
    template_name = 'user/otp_submit.html'  
    
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
                n = request.user.get_full_name()
                if n == "":
                    n=request.user.phone
                messages.success(request, f'{n}  خوش آمدید!')  
                return redirect('user:profile')  
            else:  
                form.add_error(None, 'کد وارد شده صحیح نیست یا منقضی شده است.')  
                messages.error(request, 'کد وارد شده صحیح نیست یا منقضی شده است.')  

        return render(request, self.template_name, {'form': form}) 

class SendVerifyEmailLink(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):  
        user = request.user
        if user.email is not None and user.email != '':
            if not user.email_confirmed:
                token = EmailConfirmation.generate_token(user=user)
                send_verification_email.delay(user.email, token)
                messages.error(request, 'لینک تایید ایمیل برای شما ارسال شد.')
                return redirect('user:profile')
            else:
                messages.error(request, 'ایمیل شما از قبل تایید شده بود.')
                return redirect('user:profile')
        else:
            messages.error(request, 'برای شما ایمیلی ثبت نشده است.')
            return redirect('user:profile')

class VerifyEmailView(View):

    def get(self, request, token):
        is_valid = EmailConfirmation.verify_token(token=token)
        if not is_valid:
            messages.error(request, 'لینک معتبر نیست.')
            return redirect('user:login')
        messages.success(request, 'ایمیل شما با موفقیت تایید شد.')
        return redirect('user:profile')


class ChangeEmailView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):  
        form = ChangeEmailForm(request.POST)
        if form.is_valid():  
            new_email = form.cleaned_data['new_email']  
            if User.objects.filter(email=new_email).exists():
                messages.error(request, 'ایمیل وارد شده از قبل موجود است.')
                return redirect('user:profile')
            
            token = EmailConfirmation.generate_token(user=request.user, new_email=new_email)
            send_verification_change_email.delay(new_email, token)

            messages.error(request, 'لینک تایید ایمیل برای شما ارسال شد. این لینک تا 15 دقیقه معتبر است.')
            return redirect('user:profile')
        messages.error(request, 'عملیات انجام نشد')
        return redirect('user:profile')


class VerifyChangeEmailView(View):

    def get(self, request, token):
        user_email = request.user.email
        is_valid, user_new_email = EmailConfirmation.verify_token(token=token, new_email=True)
        if not is_valid:
            messages.error(request, 'لینک معتبر نیست.')
            return redirect('user:profile')
        # send_change_email_notif.delay(user_email, user_new_email)
        messages.success(request, 'ایمیل شما با موفقیت تغییر کرد.')
        return redirect('user:profile')
    
    
class ChangePhoneRequestView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):  
        form = ChangePhoneRequestForm(request.POST)
        if form.is_valid():
            user_old_phone = request.user.phone
            new_phone = form.cleaned_data['new_phone']
            send_phone_change_codes.delay(request.user.pk, new_phone)
            messages.info(request, 'کد تایید برای شماره جدید ارسال شد. کد ارسالی تا 5 دقیقه معتبر است.')
            return redirect('user:change_phone_submit')
        else:
            messages.error(request, form.errors)
            return redirect('user:profile')
        
        
class ChangePhoneView(LoginRequiredMixin,View):
    template_name = 'user/change_phone.html'  
    
    def get(self, request, *args, **kwargs):  
        form = ChangePhoneForm()  
        return render(request, self.template_name, {'form': form}) 
    
    def post(self, request, *args, **kwargs):  
        user_old_phone = request.user.phone
        form = ChangePhoneForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            is_valid, new_pohone = ChangePhoneOTP.verify_token(request.user, token)
            
            if not is_valid:
                messages.error(request, 'کد وارد شده معتبر نیست.')
                return redirect('user:change_phone_submit')
            logMsg = {
                'title':'user phone changed',
                'user_old_phone':{user_old_phone},
                'new_phone':{new_pohone}
            }
            sp_logger.info(f"{logMsg}")
            messages.success(request, 'شماره همراه شما با موفقیت تغییر کرد.')
            return redirect('user:profile')
        else:
            messages.error(request, form.errors)
            return redirect('user:change_phone_submit')