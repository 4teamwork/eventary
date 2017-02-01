from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect

from .users import CalendarDetailView, EventCreateView
from ..forms import EventForm, FilterForm, TimeDateForm, EventGroupingForm
from ..models import Calendar, Event, EventTimeDate, Group, Secret


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

        # TODO!!! Work in progress
        if (form_event.is_valid() and form_grouping.is_valid()):

            # update the event using the form

            # update the groupings using the form

            # redirect the user to the calendar's details
            return redirect(
                'eventary:calendar-details',
                args=[self.object.pk]
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


class LandingView(TemplateView):

    template_name = 'eventary/redactors/landing.html'

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        return context


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/redactors/list_proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)
