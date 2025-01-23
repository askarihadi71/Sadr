from django.views.generic import ListView, DetailView

from user.mixins import SuperuserAccessMixin
from .models import GeneralLog, SpeicalLog


class LogListView(SuperuserAccessMixin, ListView):
    template_name = "loggerapp/log_list.html"
    queryset = GeneralLog.objects.all()
    paginate_by = 20
    context_object_name = "logs"
    
    def get_queryset(self):
        logModel = GeneralLog
        if self.request.GET.get("SP"):
            logModel = SpeicalLog


        queryset = logModel.objects.none()
        error = logModel.objects.none()
        warning = logModel.objects.none()
        debug = logModel.objects.none()
        info = logModel.objects.none()

       
        if self.request.GET.get("ERROR"):
            error = logModel.objects.filter(level='ERROR')
        if self.request.GET.get("WARNING"):
            warning = logModel.objects.filter(level='WARNING')
        if self.request.GET.get("DEBUG"):
            debug = logModel.objects.filter(level='DEBUG')
        if self.request.GET.get("INFO"):
            info = logModel.objects.filter(level='INFO')
            
        queryset = error | warning | debug | info
        return queryset
        
     
     
class LogDetailView(SuperuserAccessMixin, DetailView):
    model = GeneralLog
    template_name = "loggerapp/log.html"


class SPLogDetailView(SuperuserAccessMixin, DetailView):
    model = SpeicalLog
    template_name = "loggerapp/log.html"
   