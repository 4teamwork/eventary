from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from ..forms import EventForm, EventEditorialForm, TimeDateForm
from ..forms import EventGroupingForm, FilterForm
from ..models import Calendar, Event, EventTimeDate, Group, Host


def editorial(request, calendar_id):

    calendar = get_object_or_404(Calendar, pk=calendar_id)

    # get the querysets for the events and the proposals
    event_qs = Event.objects.filter(
        calendar=calendar_id,
        published=True
    ).order_by('title')
    proposal_qs = Event.objects.filter(
        calendar=calendar_id,
        published=False
    ).order_by('title')

    # get the filtering form and filter the query sets if possible
    filterform = FilterForm(request.GET, calendar=calendar)

    if filterform.is_valid():
        groups = filterform.groups()
        if len(groups) > 0:
            event_qs = event_qs.filter(group__in=groups).distinct()
            proposal_qs = proposal_qs.filter(group__in=groups).distinct()

    event_paginator = Paginator(event_qs, 10)

    try:
        events = event_paginator.page(request.GET.get('event_page'))
    except PageNotAnInteger:
        events = event_paginator.page(1)
    except EmptyPage:
        events = event_paginator.page(event_paginator.num_pages)

    proposal_paginator = Paginator(proposal_qs, 10)

    try:
        proposals = proposal_paginator.page(request.GET.get('proposal_page'))
    except PageNotAnInteger:
        proposals = proposal_paginator.page(1)
    except EmptyPage:
        proposals = proposal_paginator.page(proposal_paginator.num_pages)

    hosts = Host.objects.all()

    return render(request, 'eventary/editorial/index.html', {
        'calendar': calendar,
        'events': events,
        'proposals': proposals,
        'hosts': hosts,
        'filterform': filterform
    })


def event_edit(request, calendar_id, event_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    event = get_object_or_404(Event, pk=event_id, calendar=calendar_id)

    if request.method == 'POST':
        form = EventEditorialForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
    else:
        form = EventEditorialForm(instance=event)

    return render(request, 'eventary/event/edit.html', {
        'calendar': calendar,
        'event': event,
        'eventform': form
    })


def event_search(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    return render(request, 'eventary/event/search.html', {
        'calendar': calendar
    })


def event_details_ics(request, calendar_id, event_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    event = get_object_or_404(
        Event,
        pk=event_id,
        calendar=calendar,
        published=True
    )
    return render(request, 'eventary/event/details.ics', {
        'calendar': calendar,
        'event': event
    }, content_type='text/calendar')
