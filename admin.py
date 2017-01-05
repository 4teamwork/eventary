from django.contrib import admin
from .models import Calendar, Host, Event, EventTimeDate

admin.site.register(Calendar)
admin.site.register(Host)
admin.site.register(Event)
admin.site.register(EventTimeDate)
