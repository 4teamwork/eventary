from django.conf.urls import url

from .views import index
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
        r'^admins/$',
        admins.LandingView.as_view(),
        name='admins-landing'
    ),
    url(  # lists all calendars
        r'^admins/calendars/$',
        admins.CalendarListView.as_view(),
        name='admins-list_calendars'
    ),
    url(  # creates a new calendar
        r'^admins/calendar/new/$',
        admins.CalendarCreateView.as_view(),
        name='admins-create_calendar'
    ),
    url(
        r'^admins/cal_(?P<pk>[0-9]+)/delete/$',
        admins.CalendarDeleteView.as_view(),
        name='admins-delete_calendar'
    ),
    url(  # updates a calendar
        r'^admins/cal_(?P<pk>[0-9]+)/update/$',
        admins.CalendarUpdateView.as_view(),
        name='admins-update_calendar'
    ),

    # redactors views
    url(  #
        r'^redactors/$',
        redactors.LandingView.as_view(),
        name='redactors-landing'
    ),
    url(  # list all calendars
        r'^redactors/calendars/$',
        redactors.CalendarListView.as_view(),
        name='redactors-list_calendars'
    ),
    url(  # lists all proposals
        r'^cal_(?P<pk>[-1-9]+)/proposals/$',
        redactors.ProposalListView.as_view(),
        name='redactors-list_proposals'
    ),
    url(  # delete an event
        r'^cal_(?P<calendar_pk>[0-9]+)/evt_(?P<pk>[0-9]+)/delete/$',
        redactors.EventDeleteView.as_view(),
        name='redactors-delete_event'
    ),
    url(  # edits an event
        r'^cal_(?P<pk>[0-9]+)/evt_(?P<event_pk>[0-9]+)/update/$',
        redactors.EventEditView.as_view(),
        name='redactors-update_event'
    ),
    url(  # approves an event
        r'^cal_(?P<calendar_pk>[0-9]+)/evt_(?P<pk>[0-9]+)/publish/$',
        redactors.EventPublishView.as_view(),
        name='redactors-publish_event'
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
        r'cal_(?P<cal_pk>[0-9]+)/prop_(?P<pk>[0-9]+)/(?P<secret>[0-9a-f\-]{36})/$',
        users.ProposalDetailView.as_view(),
        name='users-proposal_details'
    ),

    # views that require porting to class views
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<pk>[0-9]*).ics$',
        users.EventICSExportView.as_view(),
        name='users-export_event_to_ics'
    ),
]
