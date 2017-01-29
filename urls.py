from django.conf.urls import url

from . import views
from .views import calendars, events, index

app_name = 'eventary'

urlpatterns = [

    # overview of all calendars
    url(r'^$', index.IndexView.as_view(), name='index'),

    # calemdar views
    url(  # lists all calendars
        r'^calendars/$',
        calendars.CalendarListView.as_view(),
        name='calendar-list'
    ),
    url(  # creates a new calendar
        r'^calendars/new/$',
        calendars.CalendarCreateView.as_view(),
        name='calendar-create'
    ),
    url(  # shows a calendar's details
        r'^cal_(?P<pk>[0-9]+)/$',
        calendars.CalendarDetailView.as_view(),
        name='calendar-details'
    ),
    url(  # updates a calendar
        r'^cal_(?P<pk>[0-9]+)/edit/$',
        calendars.CalendarUpdateView.as_view(),
        name='calendar-update'
    ),

    # a calendar's events and proposals
    url(  # detailed event view
        r'cal_(?P<calendar_pk>[0-9]+)/evt_(?P<pk>[0-9]*)/$',
        events.EventDetailView.as_view(),
        name='event-details'
    ),
    url(  # lists all proposals
        r'^cal_(?P<pk>[-1-9]+)/proposals/$',
        events.ProposalListView.as_view(),
        name='proposals-list'
    ),
    url(  # creates a new proposal
        r'cal_(?P<pk>[0-9]+)/new/$',
        events.EventCreateView.as_view(),
        name='event-create'
    ),
    url(  # detailed view of a proposal
        r'cal_(?P<cal_pk>[0-9]+)/prop_(?P<pk>[0+-9]+)/(?P<secret>[0-9a-f\-]{36})/$',
        events.ProposalDetailView.as_view(),
        name='proposal-details'
    ),

    # edit an event
    url(
        r'cal_(?P<pk>[0-9]*)/evt_(?P<event_pk>[0-9]*)/update/$',
        events.EventEditView.as_view(),
        name='event-edit'
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
