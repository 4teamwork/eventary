import requests

from django.core.urlresolvers import reverse
from django.views.generic.edit import DeleteView, SingleObjectMixin
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect

from .users import CalendarDetailView, EventCreateView
from .admins import LandingView as AdminLandingView
from .admins import CalendarListView as AdminCalendarListView
from ..forms import CalendarImportForm, EventsImportForm
from ..models import Event


class CalendarImportView(TemplateView):

    template_name = 'eventary/redactors/import_calendar.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarImportView, self).get_context_data(**kwargs)

        if len(self.request.GET):
            calendarimportform = CalendarImportForm(self.request.GET)
        else:
            calendarimportform = CalendarImportForm()

        if calendarimportform.is_valid():
            # prepare some google calendar api data
            google_api_data = calendarimportform.clean()
            google_api_url = 'https://www.googleapis.com/calendar/v3'
            google_api_key = 'AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs'
            date_format = '%Y-%m-%d'

            # get the events for the given calendar and time period
            google_cal = requests.get(
                '{0}/calendars/{1}/events'.format(
                    google_api_url,
                    google_api_data.get('calendar_id')
                ),
                params={
                    'timeMin': '{0}T00:00:00+01:00'.format(
                        google_api_data.get('from_date').strftime(date_format)
                    ),
                    'timeMax': '{0}T00:00:00+01:00'.format(
                        google_api_data.get('to_date').strftime(date_format)
                    ),
                    'key': google_api_key
                }
            ).json()

            # add the response to the context
            context.update({
                'google_cal': {
                    key: google_cal[key]
                    for key in ['summary', 'description']
                },
                'otherform': EventsImportForm(items=google_cal['items'])
            })

        context.update({
            'calendarimportform': calendarimportform
        })

        return context


class CalendarListView(AdminCalendarListView):

    template_name = 'eventary/redactors/list_calendars.html'


class EventDeleteView(DeleteView):

    model = Event
    template_name = 'eventary/redactors/delete_event.html'

    def get_success_url(self):
        return reverse('eventary:redirector')


class EventEditView(EventCreateView):

    template_name = 'eventary/redactors/update_event.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.event = get_object_or_404(
            Event,
            pk=kwargs.get('event_pk'),
            calendar=self.object
        )
        return super(EventEditView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context.update({'event': self.event})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.event = get_object_or_404(
            Event,
            pk=kwargs.get('event_pk'),
            calendar=self.object
        )

        # get the forms
        form_event = self.get_form_event()
        form_grouping = self.get_form_grouping()

        if (form_event.is_valid() and form_grouping.is_valid()):
            # update the event using the form
            data = form_event.clean()
            Event.objects.filter(pk=kwargs.get('event_pk')).update(**data)

            # update the groupings using the form
            data = form_grouping.clean()
            self.event.group_set.clear()
            groups = []
            for grouping in data:
                groups += data[grouping]
            self.event.group_set.set(groups)

            # redirect the user to the calendar's details
            if self.event.published:
                return redirect(
                    'eventary:users-event_details',
                    self.object.pk,
                    self.event.pk
                )
            else:
                return redirect(
                    'eventary:users-proposal_details',
                    self.object.pk,
                    self.event.pk,
                    str(self.event.secret.secret)
                )

        return super(EventEditView, self).get(request, *args, **kwargs)

    def get_form_event_initial(self):
        return {
            key: getattr(self.event, key)
            for key in [
                'title', 'host', 'location', 'image', 'document',
                'homepage', 'description', 'comment', 'prize',
                'recurring'
            ]
        }

    def get_form_grouping_initial(self):
        to_return = {}
        for group in self.event.group_set.all():
            if group.grouping.title not in to_return:
                to_return[group.grouping.title] = []
            to_return[group.grouping.title].append(group.pk)
        return to_return


class EventPublishView(SingleObjectMixin, View):

    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.published = True
        self.object.save()
        return redirect('eventary:redirector')


class LandingView(AdminLandingView):

    template_name = 'eventary/redactors/landing.html'


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/redactors/list_proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)
