from datetime import datetime
from django.views.generic import TemplateView

from ..models import Calendar, Event, EventTimeDate


class IndexView(TemplateView):

    template_name = 'eventary/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        # general context data
        context.update({
            'calendar_list': Calendar.objects.all(),
            'event_list':    Event.objects.filter(published=True),
            'proposal_list': Event.objects.filter(published=False),
            'timedate_list': EventTimeDate.objects.all()
        })

        # upcoming events and proposals
        today = datetime.today()
        context.update({
            'upcoming_event_list': Event.objects.filter(
                published=True,
                eventtimedate__start_date__gte=today,
            ).distinct(),
            'upcoming_proposal_list': Event.objects.filter(
                published=False,
                eventtimedate__start_date__gte=today,
            ).distinct()
        })

        return context
