from django.conf.urls import url

from . import views

app_name = 'eventary'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.calendar_add, name='calendar_add'),
    url(r'^list/$', views.calendar_list, name='calendar_list'),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/$',
        views.calendar_details,
        name='calendar_details'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/edit/$',
        views.calendar_edit,
        name='calendar_edit'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/proposals/$',
        views.calendar_proposals,
        name='calendar_proposals'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/add/$',
        views.event_add,
        name='event_add'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/$',
        views.event_details,
        name='event_details'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/edit/$',
        views.event_edit,
        name='event_edit'
    ),
]
