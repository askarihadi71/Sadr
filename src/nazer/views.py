from datetime import datetime
from django import forms
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView, DetailView
from django.contrib import messages

from user.mixins import SuperuserAccessMixin
from .models import Alarm,Device


class Dashbord(SuperuserAccessMixin,TemplateView):
    template_name = "nazer/dashbord.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alarms'] = Alarm.objects.all().select_related("device", "device__user").order_by("handled", "-time")
        return context


class DeviceList(SuperuserAccessMixin,ListView):
    template_name = "nazer/device_list.html"
    model = Device
    paginate_by = 10

    def get_queryset(self):  
        queryset = super().get_queryset().select_related("user")
        search_query = self.request.GET.get('search', '') 
        
        if search_query:  
            queryset = queryset.filter(  
                Q(email__icontains=search_query) |  
                Q(title__icontains=search_query) |  
                Q(description__icontains=search_query) |  
                Q(user__phone__icontains=search_query) |  
                Q(user__first_name__icontains=search_query) |  
                Q(user__last_name__icontains=search_query)  
            )  
        return queryset

    
class DeviceCreate(SuperuserAccessMixin,CreateView):
    template_name = "nazer/device_create.html"
    model = Device
    success_url = reverse_lazy("nazer:device_list")
    fields = ["title", "email", "description", "address"]

class DeveiceDelete(SuperuserAccessMixin,DeleteView):
    template_name = "nazer/device_delete.html"
    model = Device
    success_url = reverse_lazy("nazer:device_list")


class DeviceUpdate(SuperuserAccessMixin,UpdateView):
    model = Device
    fields = ["title", "email", "description", "address"]
    success_url = reverse_lazy("nazer:device_list")
    template_name = "nazer/device_create.html"



class AlarmsList(LoginRequiredMixin,ListView):
    template_name = "nazer/alarms_list.html"
    model = Alarm
    paginate_by = 20
    ordering = ("handled", "-time")

    def get_queryset(self):  
        queryset = super().get_queryset().select_related("device", "device__user")
        search_query = self.request.GET.get('search', '') 
        startTimeQ = self.request.GET.get('start-time', '') 
        endTimeQ = self.request.GET.get('end-time', '') 

        print(f'startTimeQ {startTimeQ}')

        if not self.request.user.is_superuser:
            queryset = queryset.filter(device__user=self.request.user)

        if endTimeQ != "" and startTimeQ != "":
                try:
                    from_g = datetime.strptime(startTimeQ.replace(' ', '-'), '%Y/%m/%d-%H:%M:%S')
                    to_g = datetime.strptime(endTimeQ.replace(' ', '-'), '%Y/%m/%d-%H:%M:%S')

                    queryset = queryset.filter(  
                        time__gte=timezone.make_aware(from_g),
                        time__lte=timezone.make_aware(to_g),
                    )
                except ValueError:
                    ...

        if search_query:  
            print(f"search {search_query}")
            queryset = queryset.filter(  
                Q(device__title__icontains=search_query) |  
                Q(alarm_type__icontains=search_query) |  
                Q(device_name__icontains=search_query) |  
                Q(alarm_name__icontains=search_query) |  
                Q(ip__icontains=search_query) |  
                Q(device__user__phone__icontains=search_query) |  
                Q(device__user__first_name__icontains=search_query) |  
                Q(device__user__last_name__icontains=search_query)  
            )  
        return queryset


class AlarmDelete(SuperuserAccessMixin,DeleteView):
    template_name = "nazer/device_delete.html"
    model = Alarm
    success_url = reverse_lazy("nazer:alarms_list_view")

    def get_object(self, queryset=None):
        alarm = super().get_object(queryset)
        if not self.request.user.is_superuser and alarm.device.user != self.request.user:
            messages.error(self.request, 'شما اجازه انجام این دستور را ندارید')  
            return redirect('nazer:alarms_list_view')  
        return alarm

class AlarmForm(forms.ModelForm):
    class Meta:
        model = Alarm
        exclude = ('time',)

class AlarmUpdate(SuperuserAccessMixin,UpdateView):
    model = Alarm
    form_class = AlarmForm
    success_url = reverse_lazy("nazer:alarms_list_view")
    template_name = "nazer/alarm_create.html"

    def get_object(self, queryset=None):
        alarm = super().get_object(queryset)
        if not self.request.user.is_superuser and alarm.device.user != self.request.user:
            messages.error(self.request, 'شما اجازه انجام این دستور را ندارید')  
            return redirect('nazer:alarms_list_view')  
        return alarm


class AlarmDetails(LoginRequiredMixin,DetailView):
    template_name = "nazer/alarm_delete.html"
    model = Alarm

    def get_object(self, queryset=None):
        alarm = super().get_object(queryset)

        # Check permissions
        if not self.request.user.is_superuser and alarm.device.user != self.request.user:
            messages.error(self.request, 'شما اجازه انجام این دستور را ندارید')  
            return redirect('nazer:alarms_list_view')  
        return alarm
