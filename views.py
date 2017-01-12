import calendar as pycal
import datetime as pydt
import math

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .forms import CalendarForm, EventForm, EventEditorialForm, TimeDateForm
from .forms import EventGroupingForm, FilterForm
from .models import Calendar, Event, EventTimeDate, Group, Host


def index(request):
    return render(request, 'eventary/index.html', {})


def calendar_add(request):
    if request.method == 'POST':
        form = CalendarForm(request.POST)

        if form.is_valid():
            calendar = form.save()
            return HttpResponseRedirect(reverse(
                'eventary:calendar_details',
                args=[calendar.pk]
            ))

    else:
        form = CalendarForm()

    return render(request, 'eventary/calendar/add.html', {
        'calendarform': form
    })


def calendar_list(request):
    calendars = Calendar.objects.all()
    return render(request, 'eventary/calendar/list.html', {
        'calendars': calendars
    })


def calendar_details(request, calendar_id):
    # dropout if the calendar does not exist
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    # if a date is given, use the given date, else use today
    now = pydt.date.today()
    year = int(request.GET.get('year', default=now.year))
    month = int(request.GET.get('month', default=now.month))
    date = pydt.date(year, month, 1)

    # compute the first day of the upcoming month and the last day of
    # the previous month
    last_previous = pydt.date(year, month, 1) - pydt.timedelta(days=1)
    first_next = pydt.date(
        year + math.ceil(((month + 1) / 12) - 1),
        (month + 1) % 12 or 12,
        1
    )

    # collect the event time dates in the previewed month and paginate them
    timedate_qs = EventTimeDate.objects.filter(
        Q(event__published=True) & (
            Q(start_date__range=(last_previous, first_next)) |
            Q(end_date__range=(last_previous, first_next))
        )
    )
    timedate_paginator = Paginator(timedate_qs, 10)
    try:
        timedates = timedate_paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        timedates = timedate_paginator.page(1)
    except EmptyPage:
        timedates = timedate_paginator.page(timedate_paginator.num_pages)

    # filter the events in the previewed month and paginate
    event_qs = Event.objects.filter(
        calendar=calendar_id,
        published=True,
        eventtimedate__in=timedate_qs
    ).distinct()

    if request.method == 'GET':
        filterform = FilterForm(request.GET, calendar=calendar)
        if filterform.is_valid():
            # get the groups selected in the filter
            groups = filterform.groups()
            # filter the events
            if len(groups) > 0:
                event_qs = event_qs.filter(group__in=groups)
    else:
        filterform = FilterForm(calendar=calendar)

    event_paginator = Paginator(event_qs, 10)
    try:
        events = event_paginator.page(request.GET.get('event_page'))
    except PageNotAnInteger:
        events = event_paginator.page(1)
    except EmptyPage:
        events = event_paginator.page(event_paginator.num_pages)

    # get the date's calendar sorted by weeks
    _pycal = pycal.Calendar().monthdayscalendar(year, month)

    # now sort the events into a table
    table = []
    for week in _pycal:
        _week = []
        for day in week:
            if day == 0:
                # no events on no days
                _week.append((None, []))
            else:
                _day = pydt.date(year, month, day)

                # now create a list of events sorted by date
                _week.append((day, list(event_qs.filter(
                    Q(eventtimedate__start_date=_day) |
                    Q(eventtimedate__end_date=_day)
                ).distinct())))
        table.append(_week)

    return render(request, 'eventary/calendar/details.html', {
        'calendar': calendar,
        'events': events,
        'timedates': timedates,
        'overview': table,
        'previous': last_previous,
        'date': date,
        'next': first_next,
        'filterform': filterform
    })


def calendar_edit(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    if request.method == 'POST':
        form = CalendarForm(request.POST, instance=calendar)
        if form.is_valid():
            form.save()
    else:
        form = CalendarForm(instance=calendar)

    return render(request, 'eventary/calendar/edit.html', {
        'calendar': calendar,
        'calendarform': form
    })


def calendar_proposals(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    events = Event.objects.filter(
        calendar=calendar_id,
        published=False
    ).order_by('-proposed', 'title')

    return render(request, 'eventary/calendar/proposals.html', {
        'calendar': calendar,
        'events': events
    })


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
                'eventary:event_details',
                args=[calendar.pk, event.pk]
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
    return render(request, 'eventary/event/details.html', {
        'calendar': calendar,
        'event': event
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
    })
