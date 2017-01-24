from django import template
from ..models import Event

register = template.Library()


@register.filter(name='to_date')
def date(value):
    """Returns the date of an event as a string"""
    result = ""
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

                result = "{0} - {1}".format(
                    timedate.start_date.strftime(startformat),
                    timedate.end_date.strftime("%d.%m.%Y")
                )
            else:
                result = "{0}".format(timedate.start_date.strftime("%d.%m.%Y"))
    return result


@register.filter(name='to_time')
def time(value):
    """Returns the time of an event as a string"""
    result = ""
    if isinstance(value, Event):
        timedates = value.eventtimedate_set.all()
        for timedate in timedates:
            if (
                timedate.end_time is not None and
                timedate.start_time is not None
            ):
                result += "{0} - {1}".format(
                    timedate.start_time.strftime("%H:%M"),
                    timedate.end_time.strftime("%H:%M")
                )
            else:
                result += "{0}".format(timedate.start_date)

    return result


@register.simple_tag
def url_replace(request, field, value):
    """Replaces a specific GET parameter"""
    _dict = request.GET.copy()
    _dict[field] = value
    return _dict.urlencode()
