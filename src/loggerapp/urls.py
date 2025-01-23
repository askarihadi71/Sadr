from django.urls import path, include
from . views import LogListView, LogDetailView, SPLogDetailView

app_name = 'loggerapp'
urlpatterns = [
    
    path('', LogListView.as_view(), name="logs"),
    path('logs/<int:pk>/', LogDetailView.as_view(), name="log_details"),
    path('logs/sp/<int:pk>/', SPLogDetailView.as_view(), name="splog_details"),
]