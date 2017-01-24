from django.views.generic import DetailView

from .calendars import CalendarDetailView
from ..models import Event


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/events/proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)


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
