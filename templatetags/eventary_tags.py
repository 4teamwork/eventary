from django import template
from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string

from ..models import Calendar, Event

register = template.Library()


@register.filter(name='to_full_date')
def full_date(value):
    results = []
    if isinstance(value, Event):
        timedates = value.eventtimedate_set.all()
        for timedate in timedates:

            if (
                timedate.end_date is not None and
                timedate.end_date != timedate.start_date
            ):

                # generally, the start format is just the day, but we
                # might change it if some of the values do not coincide
                startformat = "%d."
                if timedate.start_date.month != timedate.end_date.month:
                    startformat += "%m."
                if timedate.start_date.year != timedate.end_date.year:
                    startformat += "%Y"

                results.append("{0}{1} - {2}{3}".format(
                    timedate.start_date.strftime(startformat),
                    (timedate.start_time and
                        timedate.start_time.strftime(" %H:%M") or ''),
                    timedate.end_date.strftime("%d.%m.%Y"),
                    (timedate.end_time and
                        timedate.end_time.strftime(" %H:%M") or '')
                ))
            else:
                results.append("{0}{1}{2}".format(
                    timedate.start_date.strftime("%d.%m.%Y"),
                    (timedate.start_time and
                        timedate.start_time.strftime(" %H:%M") or ''),
                    (timedate.end_time and
                        timedate.end_time.strftime(" - %H:%M") or '')
                ))
    return len(results) and ", ".join(results) or ""


@register.simple_tag
def url_replace(request, field, value):
    """Replaces a specific GET parameter"""
    _dict = request.GET.copy()
    _dict[field] = value
    return _dict.urlencode()


@register.filter(name='join')
def join(value, arg):
    return str(arg).join([
        getattr(g, 'title', str(g)) for g in value
    ])


@register.filter(name='navigation')
def navigation(value):

    user_type = 'users'
    if isinstance(value, User):

        admins = Group.objects.get(name='eventary_admins')
        redactors = Group.objects.get(name='eventary_redactors')

        if redactors in value.groups.all():
            user_type = 'redactors'
        elif admins in value.groups.all():
            user_type = 'admins'

    return render_to_string('eventary/navigation/{0}.html'.format(user_type))


@register.filter(name='actions')
def actions(value, arg=None):

    user_type = 'users'
    if arg is not None and isinstance(arg, User):

        admins = Group.objects.get(name='eventary_admins')
        redactors = Group.objects.get(name='eventary_redactors')

        if redactors in arg.groups.all():
            user_type = 'redactors'
        elif admins in arg.groups.all():
            user_type = 'admins'

    if isinstance(value, Calendar):
        return render_to_string(
            'eventary/actions/calendars_{0}.html'.format(user_type),
            context={'calendar': value}
        )

    if isinstance(value, Event):
        if value.published:
            return render_to_string(
                'eventary/actions/events_{0}.html'.format(user_type),
                context={'event': value}
            )
        else:
            return render_to_string(
                'eventary/actions/proposals_{0}.html'.format(user_type),
                context={'event': value}
            )
