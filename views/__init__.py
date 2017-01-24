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


def event_add(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if request.method == 'POST':
        eventform = EventForm(request.POST, request.FILES)
        timedateform = TimeDateForm(request.POST)
        groupingform = EventGroupingForm(request.POST, calendar=calendar)

        if (
            eventform.is_valid() and
            timedateform.is_valid() and
            groupingform.is_valid()
        ):

            # prepare the event and store it
            event = eventform.save(commit=False)
            event.calendar = calendar
            event.published = False
            event.save()

            # create the time date objects for te event
            timedatedata = timedateform.clean()
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
            groupingdata = groupingform.clean()
            for grouping in groupingdata:
                for group_pk in groupingdata[grouping]:
                    group = get_object_or_404(
                        Group,
                        pk=int(group_pk),
                        grouping__title=grouping
                    )

                    group.events.add(event)
                    group.save()

            return HttpResponseRedirect(reverse(
                'eventary:calendar-details',
                args=[calendar.pk]
            ))

    else:
        eventform = EventForm()
        timedateform = TimeDateForm()
        groupingform = EventGroupingForm(calendar=calendar)

    return render(request, 'eventary/event/add.html', {
        'calendar': calendar,
        'eventform': eventform,
        'timedateform': timedateform,
        'groupingform': groupingform
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


def event_details(request, calendar_id, event_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    event = get_object_or_404(
        Event,
        pk=event_id,
        calendar=calendar,
        published=True
    )
    timedates = EventTimeDate.objects.filter(event=event)
    groupings = {}
    for group in event.group_set.distinct():
        if group.grouping not in groupings:
            groupings[group.grouping] = []
        groupings[group.grouping].append(group)
    return render(request, 'eventary/event/details.html', {
        'calendar': calendar,
        'event': event,
        'timedates': timedates,
        'groupings': groupings
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
