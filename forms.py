from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'host', 'location', 'image', 'document',
            'homepage', 'description', 'comment', 'prize'
        ]


class TimeDateForm(forms.Form):
    start_date_time = forms.DateTimeField(widget=DateTimePicker(options={
        "format": "YYYY-MM-DD HH:mm"
    }))
    end_date_time = forms.DateTimeField(widget=DateTimePicker(options={
        "format": "YYYY-MM-DD HH:mm",
    }))
