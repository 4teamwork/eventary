import calendar as pycal
import datetime as pydt
import math

from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render

from .forms import EventForm, TimeDateForm
from .models import Calendar, Event


def index(request):
    return render(request, 'cal/index.html', {})


def calendar_list(request):
    calendars = Calendar.objects.all()
    return render(request, 'cal/calendar_list.html', {
        'calendars': calendars
    })


def calendar_details(request, calendar_id):
    # return a 404 object if the calendar does not exist
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    # the default view shows the actual month
    now = pydt.datetime.now()

    # but another month can be set through get variables
    year = int(request.GET.get('year', default=now.year))
    month = int(request.GET.get('month', default=now.month))

    # to filter the right events we need the last day of the previous month
    # and the first day of the upcoming month
    last_previous = pydt.date(year, month, 1) - pydt.timedelta(days=1)
    # computing the first day of the upcoming month is slightly more complex
    # (since timedelta can't deal with months)
    first_next = pydt.date(
        # compute the year of the next month
        year + math.ceil(((month + 1) / 12) - 1),
        # compute the number of the next month
        (month + 1) % 12 or 12,
        1
    )

    # now get all the events for the selected year / month
    events = Event.objects.filter(
        calendar=calendar_id
    ).exclude(
        eventtimedate__start_date__gte=first_next
    ).exclude(
        eventtimedate__end_date__lte=last_previous
    ).distinct()

    # get the calendar for the given year and month
    # the resulting array of weeks of the month is useful
    # to arrange the calendar's events
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
                # similar to last_previous and first_next, find the limits
                lower = pydt.date(year, month, day) - pydt.timedelta(days=1)
                upper = pydt.date(year, month, day) + pydt.timedelta(days=1)

                # now create a list of events sorted by date
                _week.append((day, list(events.exclude(
                    eventtimedate__start_date__gte=upper
                ).exclude(
                    eventtimedate__end_date__lte=lower
                ))))
        table.append(_week)

    return render(request, 'cal/calendar_details.html', {
        'calendar': calendar,
        'events': events,
        'overview': table,
        'previous': last_previous,
        'next': first_next
    })


def event_add(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if request.method == 'POST':
        eventform = EventForm(request.POST, request.FILES)
        timedateform = TimeDateForm(request.POST)

        if eventform.is_valid() and timedateform.is_valid():
            pass
            # todo: check if the forms in the formset are valid
            # todo: generate the events and their corresponding eventdatetime
    else:
        eventform = EventForm()
        timedateform = TimeDateForm()

    return render(request, 'cal/event_add.html', {
        'calendar': calendar,
        'eventform': eventform,
        'timedateform': timedateform
    })


def event_list(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    return render(request, 'cal/list.html', {
        'calendar': calendar
    })


def event_details(request, calendar_id, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'cal/event_details.html', {
        'event': event
    })
