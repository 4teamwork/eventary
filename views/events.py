from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404

from .calendars import CalendarDetailView
from ..forms import EventForm, TimeDateForm, EventGroupingForm
from ..models import Calendar, Event, EventTimeDate, Group


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/events/proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)


class EventCreateView(SingleObjectMixin, TemplateView):

    model = Calendar
    template_name = 'eventary/events/create.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EventCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # get the forms
        form_event = self.get_form_event()
        form_timedate = self.get_form_timedate()
        form_grouping = self.get_form_grouping()

        if (
            form_event.is_valid() and
            form_timedate.is_valid() and
            form_grouping.is_valid()
        ):
            # prepare the event and store it
            event = form_event.save(commit=False)
            event.calendar = self.object
            event.published = False
            event.save()

            # create the time date objects for the event
            timedatedata = form_timedate.clean()
            timedate = EventTimeDate()
            timedate.event = event
            timedate.start_date = timedatedata['start_date']

            if timedatedata['start_time'] is not None:
                timedate.start_time = timedatedata['start_time']

            if timedatedata['end_date'] is not None:
                timedate.end_date = timedatedata['end_date']

            if timedatedata['end_time'] is not None:
                timedate.end_time = timedatedata['end_time']

            timedate.save()

            # associate the event to the groups given by the groupingform
            groupingdata = form_grouping.clean()
            for grouping in groupingdata:
                for group_pk in groupingdata[grouping]:
                    group = get_object_or_404(
                        Group,
                        pk=int(group_pk),
                        grouping__title=grouping
                    )

                    group.events.add(event)
                    group.save()

            # redirect the user to the calendar's details
            return HttpResponseRedirect(reverse(
                'eventary:calendar-details',
                args=[self.object.pk]
            ))

        return super(EventCreateView, self).get(request, *args, **kwargs)

    def get_form_event(self):
        get_initial = getattr(self, 'get_form_event_initial', lambda: {})
        if self.request.method == 'POST':
            self.event_form = EventForm(
                self.request.POST,
                initial=get_initial()
            )
        else:
            self.event_form = EventForm(initial=get_initial())
        return self.event_form

    def get_form_timedate(self):
        get_initial = getattr(self, 'get_form_timedate_initial', lambda: {})
        if self.request.method == 'POST':
            self.timedate_form = TimeDateForm(
                self.request.POST,
                initial=get_initial()
            )
        else:
            self.timedate_form = TimeDateForm(initial=get_initial())
        return self.timedate_form

    def get_form_grouping(self):
        get_initial = getattr(self, 'get_form_grouping_initial', lambda: {})
        if self.request.method == 'POST':
            self.grouping_form = EventGroupingForm(
                self.request.POST,
                calendar=self.object,
                initial=get_initial()
            )
        else:
            self.grouping_form = EventGroupingForm(
                calendar=self.object,
                initial=get_initial()
            )
        return self.grouping_form

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)

        context.update({
            'eventform': self.get_form_event(),
            'timedateform': self.get_form_timedate(),
            'groupingform': self.get_form_grouping()
        })

        return context


class EventEditView(EventCreateView):

    template_name = 'eventary/events/edit.html'

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
            return HttpResponseRedirect(reverse(
                'eventary:calendar-details',
                args=[self.object.pk]
            ))

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


class EventDetailView(DetailView):

    model = Event
    template_name = 'eventary/events/details.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        groupings = {}
        for group in self.object.group_set.distinct():
            if group.grouping not in groupings:
                groupings[group.grouping] = []
            groupings[group.grouping].append(group)

        context.update({
            'timedates': self.object.eventtimedate_set.all(),
            'groupings': groupings
        })

        return context
