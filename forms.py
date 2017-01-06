from bootstrap3_datetime.widgets import DateTimePicker
from django import forms

from .models import Event, EventTimeDate


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'host', 'location', 'image', 'document',
            'homepage', 'description', 'comment', 'prize'
        ]


class EventTimeDateForm(forms.Form):
    start = forms.DateTimeField(widget=DateTimePicker())
    end = forms.DateTimeField(widget=DateTimePicker())
