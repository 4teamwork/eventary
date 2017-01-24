from django.conf.urls import url

from . import views
from .views import calendars, events, index

app_name = 'eventary'

urlpatterns = [

    # lists the events of all calendars
    url(r'^$', index.IndexView.as_view(), name='index'),

    # lists the calendars
    url(
        r'^calendars/$',
        calendars.CalendarListView.as_view(),
        name='calendar-list'
    ),

    # creates a new calendar
    url(
        r'^calendars/new/$',
        calendars.CalendarCreateView.as_view(),
        name='calendar-create'
    ),

    # shows a calendar's detailed view
    url(
        r'^cal_(?P<pk>[0-9]*)/$',
        calendars.CalendarDetailView.as_view(),
        name='calendar-details'
    ),

    # updates a calendar
    url(
        r'^cal_(?P<pk>[0-9]*)/edit/$',
        calendars.CalendarUpdateView.as_view(),
        name='calendar-update'
    ),

    # lists the proposals of a calendar
    url(
        r'^proposals/cal_(?P<pk>[0-9]*)/$',
        events.ProposalListView.as_view(),
        name='proposals-list'
    ),

    url(
        r'cal_(?P<calendar_pk>[0-9]*)/evt_(?P<pk>[0-9]*)/$',
        events.EventDetailView.as_view(),
        name='event-details'
    ),



    # creates a new event
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/new/$',
        views.event_add,
        name='event_add'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/$',
        views.event_details,
        name='event_details'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*).ics$',
        views.event_details_ics,
        name='event_details_ics'
    ),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/edit/$',
        views.event_edit,
        name='event_edit'
    ),
    url(
        r'^editorial/cal_(?P<calendar_id>[0-9]*)/$',
        views.editorial,
        name='editorial'
    ),
]
