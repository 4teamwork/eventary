from django.conf.urls import url

from . import views
from .views import calendars, events, index
from .views import admins, redactors, users

app_name = 'eventary'

urlpatterns = [

    # redirects users to theyr landing page
    url(
        r'^$',
        index.UserRedirectView.as_view(),
        name='redirector'
    ),

    # admin views
    url(  # overview of all calendars
        r'^calendars/$',
        admins.LandingView.as_view(),
        name='admins-landing'
    ),
    url(  # creates a new calendar
        r'^calendars/new/$',
        admins.CalendarCreateView.as_view(),
        name='admins-create_calendar'
    ),
    url(  # updates a calendar
        r'^calendars/cal_(?P<pk>[0-9]+)/edit/$',
        admins.CalendarUpdateView.as_view(),
        name='admins-update_calendar'
    ),

    # redactors views
    url(  #
        r'^redactors/$',
        redactors.LandingView.as_view(),
        name='redactors-landing'
    ),
    url(  # lists all proposals
        r'^cal_(?P<pk>[-1-9]+)/proposals/$',
        redactors.ProposalListView.as_view(),
        name='redactors-list_proposals'
    ),
    url(  # edits an event
        r'cal_(?P<pk>[0-9]*)/evt_(?P<event_pk>[0-9]*)/update/$',
        events.EventEditView.as_view(),
        name='redactors-update_event'
    ),

    # users views
    url(  # landing page
        r'^users/$',
        users.LandingView.as_view(),
        name='users-landing'
    ),
    url(  # shows a calendar's details
        r'^cal_(?P<pk>[0-9]+)/$',
        users.CalendarDetailView.as_view(),
        name='users-calendar_details'
    ),
    url(  # creates a new proposal
        r'cal_(?P<pk>[0-9]+)/new/$',
        users.EventCreateView.as_view(),
        name='users-create_event'
    ),
    url(  # detailed event view
        r'cal_(?P<calendar_pk>[0-9]+)/evt_(?P<pk>[0-9]*)/$',
        users.EventDetailView.as_view(),
        name='users-event_details'
    ),
    url(  # detailed view of a proposal
        r'cal_(?P<cal_pk>[0-9]+)/prop_(?P<pk>[0+-9]+)/(?P<secret>[0-9a-f\-]{36})/$',
        users.ProposalDetailView.as_view(),
        name='users-proposal_details'
    ),

    # views that require porting to class views
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*).ics$',
        views.event_details_ics,
        name='event_details_ics'
    ),
]
