from django.urls import path, include
from .views import Dashbord, DeviceList, DeviceCreate, DeveiceDelete, DeviceUpdate, AlarmsList, AlarmDelete, AlarmUpdate, AlarmDetails

app_name="nazer"
urlpatterns = [
    path("", Dashbord.as_view(), name="dahsbord"),

    path("devices", DeviceList.as_view(), name="device_list"),
    path("devices/create", DeviceCreate.as_view(), name="device_create"),
    path("devices/delete/<int:pk>", DeveiceDelete.as_view(), name="device_delete"),
    path("devices/update/<int:pk>", DeviceUpdate.as_view(), name="device_update"),


    path("alarms", AlarmsList.as_view(), name="alarms_list_view"),
    path("alarms/delete/<int:pk>", AlarmDelete.as_view(), name="alarm_delete"),
    path("alarms/update/<int:pk>", AlarmUpdate.as_view(), name="alarm_update"),
    path("alarms/<int:pk>", AlarmDetails.as_view(), name="alarm_details_view"),

    path("api/", include("nazer.api.urls"))
]
