from django.shortcuts import get_object_or_404, render
from .models import Event


def index(request):
    return render(request, 'cal/index.html', {})


def details(request, calendar_id, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'cal/details.html', {
        'event': event
    })
