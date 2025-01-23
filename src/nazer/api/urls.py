from django.urls import path
from .apis import AlarmDetails, Test,AlarmsList, AlarmStatusChange, Overview, SetOwnerAPIView, ClearOwnerAPIView


urlpatterns = [
    path("overview/", Overview.as_view(), name="overview"),

    path("alarms/", AlarmsList.as_view(), name="alarms_list"),
    path("alarm/<int:pk>/", AlarmDetails.as_view(), name="alarm_details"),
    path("alarm/change_status/<int:pk>/", AlarmStatusChange.as_view(), name="alarm_change_status"),

    path('set-owner/', SetOwnerAPIView.as_view(), name='set_owner'),
    path('clear-owner/', ClearOwnerAPIView.as_view(), name='Clear_owner'),

    path("test/", Test.as_view(), name="test")
]
