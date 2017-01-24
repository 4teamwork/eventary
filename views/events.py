from django.views.generic import DetailView

from .calendars import CalendarDetailView


class ProposalListView(CalendarDetailView):

    template_name = 'eventary/events/proposals.html'

    def get_queryset(self):
        return self.object.event_set.filter(published=False)


class EventDetailView(DetailView):

    template_name = 'eventary/events/details.html'
