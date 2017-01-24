from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView

from ..forms import GenericFilterForm
from ..models import Calendar, Event, EventTimeDate


class IndexView(TemplateView):

    template_name = 'eventary/index.html'

    def get_form(self):
        if len(self.request.GET):
            form = GenericFilterForm(self.request.GET, prefix="filter")
        else:
            form = GenericFilterForm(prefix="filter")
        return form

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

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
        context.update({
            'form': form
        })
        if form.is_valid():
            data = form.clean()
            if data['from_date'] is not None:
                event_list = event_list.exclude(
                    eventtimedate__start_date__lt=data['from_date']
                )
                proposal_list = proposal_list.exclude(
                    eventtimedate__start_date__lt=data['from_date']
                )
            if data['to_date'] is not None:
                event_list = event_list.exclude(
                    eventtimedate__start_date__gt=data['to_date']
                )
                proposal_list = proposal_list.exclude(
                    eventtimedate__start_date__gt=data['to_date']
                )
            groups = form.groups()
            if len(groups) > 0:
                event_list = event_list.filter(group__in=groups)
                proposal_list = proposal_list.filter(group__in=groups)

        # create some paginators for the event lists
        event_paginator = Paginator(event_list, 25)
        proposal_paginator = Paginator(proposal_list, 25)

        # paginate the events [!! overrides event_list !!]
        event_page = self.request.GET.get('event_page', 1)
        try:
            event_list = event_paginator.page(event_page)
        except PageNotAnInteger:
            event_list = event_paginator.page(1)
        except EmptyPage:
            event_list = event_paginator.page(event_paginator.num_pages)

        # paginate the proposals [!! overrides proposal_list !!]
        proposal_page = self.request.GET.get('proposal_page', 1)
        try:
            proposal_list = proposal_paginator.page(proposal_page)
        except PageNotAnInteger:
            proposal_list = proposal_paginator.page(1)
        except EmptyPage:
            proposal_list = proposal_paginator.page(
                proposal_paginator.num_pages
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
