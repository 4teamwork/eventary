from django.contrib import admin
from .models import Calendar, Host, Event, EventTimeDate
from .models import GroupingType, Grouping, Group

admin.site.register(Calendar)
admin.site.register(Host)
admin.site.register(Event)
admin.site.register(EventTimeDate)

admin.site.register(GroupingType)
admin.site.register(Grouping)
admin.site.register(Group)
