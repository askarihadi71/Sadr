from django.contrib import admin
from .models import GeneralLog, SpeicalLog
# Register your models here.

class LogAdmin(admin.ModelAdmin):
    search_fields = ('level','message',)
    list_display = ['time', 'level', 'message',  ]
    list_filter = ('level',)
    fields = ['level', 'message',  ]


admin.site.register(GeneralLog, LogAdmin)
admin.site.register(SpeicalLog, LogAdmin)
