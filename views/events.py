from django.views.generic import DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from .calendars import CalendarDetailView
from ..forms import EventForm, TimeDateForm, EventGroupingForm
from ..models import Calendar, Event


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/events/proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)


class EventCreateView(SingleObjectMixin, TemplateView):

    model = Calendar
    template_name = 'eventary/events/create.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Calendar.objects.all())
        return super(EventCreateView, self).get(request, *args, **kwargs)

    def get_form_event(self):
        if self.request.method == 'POST':
            self.event_form = EventForm(self.request.POST)
        else:
            self.event_form = EventForm()
        return self.event_form

    def get_form_timedate(self):
        if self.request.method == 'POST':
            self.timedate_form = TimeDateForm(self.request.POST)
        else:
            self.timedate_form = TimeDateForm()
        return self.timedate_form

    def get_form_grouping(self):
        if self.request.method == 'POST':
            self.grouping_form = EventGroupingForm(self.request.POST)
        else:
            self.grouping_form = EventGroupingForm()
        return self.grouping_form

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)

        context.update({
            'eventform': None,
            'timedateform': None,
            'groupingform': None
        })

        return context


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
