from django.conf.urls import url

from . import views

app_name = 'cal'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/$', views.calendar_list, name='calendar_list'),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/$',
        views.calendar_details,
        name='calendar_details'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/$',
        views.details,
        name='event_details'
    ),
]
