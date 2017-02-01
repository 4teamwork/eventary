from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from ..forms import CalendarForm, GenericFilterForm
from ..models import Calendar, Event, EventTimeDate


class CalendarCreateView(CreateView):

    form_class = CalendarForm
    model = Calendar
    template_name = 'eventary/admins/create_calendar.html'

    def get_success_url(self):
        """Returns the user to the details view of the created calendar."""

        # todo: create a secret and create a link with 'n' previews per day
        return reverse(
            'eventary:calendar-details',
            args=[self.object.pk]
        )


class CalendarUpdateView(UpdateView):

    form_class = CalendarForm
    model = Calendar
    template_name = 'eventary/admins/update_calendar.html'


class LandingView(TemplateView):

    template_name = 'eventary/admins/landing.html'

    def filter_qs(self, qs):

        if self.form.is_valid():
            data = self.form.clean()
            if data['from_date'] is not None:
                qs = qs.exclude(
                    eventtimedate__start_date__lt=data['from_date']
                )
            if data['to_date'] is not None:
                qs = qs.exclude(
                    eventtimedate__start_date__gt=data['to_date']
                )
            groups = self.form.groups()
            if len(groups) > 0:
                qs = qs.filter(group__in=groups)
        return qs

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)

        # general context data
        context.update({
            'calendar_list':  Calendar.objects.all(),
            'event_count':    Event.objects.filter(published=True).count(),
            'proposal_count': Event.objects.filter(published=False).count(),
            'timedate_count': EventTimeDate.objects.count()
        })

        # upcoming events and proposals
        today = datetime.today()
        event_list = Event.objects.filter(
            published=True,
            eventtimedate__start_date__gte=today,
        ).distinct()
        proposal_list = Event.objects.filter(
            published=False,
            eventtimedate__start_date__gte=today,
        ).distinct()

        # filter the events and proposals
        form = self.get_form()
        context.update({'form': form})
        event_list = self.filter_qs(event_list)
        proposal_list = self.filter_qs(proposal_list)

        # create some paginators
        event_list, event_paginator = self.paginate_qs(
            event_list,
            prefix='event'
        )
        proposal_list, proposal_paginator = self.paginate_qs(
            proposal_list,
            prefix='proposal'
        )

        context.update({
            'event_list':    event_list,
            'proposal_list': proposal_list
        })

        context.update({
            'event_paginator': event_paginator,
            'proposal_paginator': proposal_paginator
        })

        return context

    def get_form(self):
        if len(self.request.GET):
            self.form = GenericFilterForm(self.request.GET, prefix='filter')
        else:
            self.form = GenericFilterForm(prefix='filter')
        return self.form

    def paginate_qs(self, qs, prefix='paginator'):
        paginator = Paginator(qs, 25)

        page = self.request.GET.get('{0}_page'.format(prefix), 1)
        try:
            obj_list = paginator.page(page)
        except PageNotAnInteger:
            obj_list = paginator.page(1)
        except EmptyPage:
            obj_list = paginator.page(paginator.num_pages)

        return obj_list, paginator
