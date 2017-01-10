import calendar as pycal
import datetime as pydt
import math

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .forms import CalendarForm, EventForm, TimeDateForm, EventGroupingForm
from .models import Calendar, Event, EventTimeDate, Group


def index(request):
    return render(request, 'cal/index.html', {})


def calendar_list(request):
    calendars = Calendar.objects.all()
    return render(request, 'cal/calendar/list.html', {
        'calendars': calendars
    })


def calendar_details(request, calendar_id):
    """Displays an overview of the selected calendar.

    The monthly overview is completed with a search field."""
    # return a 404 object if the calendar does not exist
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    # the default view shows the actual month
    now = pydt.date.today()

    # but another month can be set through get variables - for "pagination"
    year = int(request.GET.get('year', default=now.year))
    month = int(request.GET.get('month', default=now.month))

    # rewrite 'now' with the given year and month
    now = pydt.date(year, month, 1)

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
        published=False
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
                ).distinct())))
        table.append(_week)

    return render(request, 'cal/calendar/details.html', {
        'calendar': calendar,
        'events': events,
        'overview': table,
        'previous': last_previous,
        'now': now,
        'next': first_next
    })


def calendar_edit(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    if request.method == 'POST':
        form = CalendarForm(request.POST)
    else:
        form = CalendarForm(instance=calendar)
        form.init_fields()

    return render(request, 'cal/calendar/edit.html', {
        'calendar': calendar,
        'form': form
    })


def event_add(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if request.method == 'POST':
        eventform = EventForm(request.POST, request.FILES)
        timedateform = TimeDateForm(request.POST)
        groupingform = EventGroupingForm(request.POST)
        groupingform.init_fields(calendar_id)

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
            timedate.start_date = timedatedata['start_date_time'].date()
            timedate.start_time = timedatedata['start_date_time'].time()
            timedate.end_date = timedatedata['end_date_time'].date()
            timedate.end_time = timedatedata['end_date_time'].time()
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
                'cal:event_details',
                args=[calendar.pk, event.pk]
            ))

    else:
        eventform = EventForm()
        timedateform = TimeDateForm()
        groupingform = EventGroupingForm()
        groupingform.init_fields(calendar_id)

    return render(request, 'cal/event/add.html', {
        'calendar': calendar,
        'eventform': eventform,
        'timedateform': timedateform,
        'groupingform': groupingform
    })


def event_search(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    return render(request, 'cal/event/search.html', {
        'calendar': calendar
    })


def event_details(request, calendar_id, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'cal/event/details.html', {
        'event': event
    })
