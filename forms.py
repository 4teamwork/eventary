from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

from .models import Calendar, Grouping, Group, Event


class FilterForm(forms.Form):

    def init_fields(self, calendar_id):

        # get the groups
        _groups = Group.objects.filter(
            grouping__calendars=calendar_id
        ).order_by('grouping').distinct()

        # group the groups by groupings
        _groupings = {}
        for group in _groups:
            # if the group was not added before, do it now
            if group.grouping not in _groupings:
                _groupings[group.grouping] = []
            _groupings[group.grouping].append(group)

        # generate choices using the sorted groupings
        _choices = {
            grouping: [
                (group.pk, group.title) for group in _groupings[grouping]
            ] for grouping in _groupings
        }

        # Now that we have the choices, generate MultipleChoiceFields with them
        _fields = {
            grouping.title: forms.MultipleChoiceField(
                required=False,
                widget=forms.CheckboxSelectMultiple,
                choices=_choices[grouping]
            ) for grouping in _groupings
        }

        self.fields.update(_fields)


class CalendarForm(forms.ModelForm):

    groupings = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            (grouping.pk, grouping.title)
            for grouping in Grouping.objects.all()
        ]
    )

    def init_fields(self):
        self.fields['groupings'].initial = [
            grouping.pk for grouping in Grouping.objects.filter(
                calendars=self.instance.pk
            )
        ]

    class Meta:
        model = Calendar
        fields = ['title']


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


class EventGroupingForm(forms.Form):

    def init_fields(self, calendar_id):

        # First we need to get the available groups
        _groups = Group.objects.filter(
            grouping__calendars=calendar_id
        ).order_by('grouping').distinct()

        # Now we need to group the possible choices
        self._groupings = {}
        for group in _groups:
            # if the group was not added before, do it now
            if group.grouping not in self._groupings:
                self._groupings[group.grouping] = []
            self._groupings[group.grouping].append(group)

        # Generate choices using the sorted groupings
        self._choices = {
            grouping: [
                (group.pk, group.title) for group in self._groupings[grouping]
            ] for grouping in self._groupings
        }

        # Now that we have the choices, generate MultipleChoiceFields with them
        _fields = {
            grouping.title: forms.MultipleChoiceField(
                required=False,
                widget=forms.CheckboxSelectMultiple,
                choices=self._choices[grouping]
            ) for grouping in self._groupings
        }

        # now generate the form
        self.fields.update(_fields)
