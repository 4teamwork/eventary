from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

from .models import Group, Event


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
    groups = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple
    )


def event_grouping_form_factory(calendar_id):

    # First we need to get the available groups
    groups = Group.objects.filter(
        grouping__calendars=calendar_id
    ).order_by('grouping').distinct()

    # Now we need to group the possible choices
    groupings = {}
    for group in groups:
        # if the group was not added before, do it now
        if group.grouping not in groupings:
            groupings[group.grouping] = []
        groupings[group.grouping].append(group)

    # Generate choices using the sorted groupings
    choices = {
        grouping: [
            (group.pk, group.title) for group in groupings[grouping]
        ] for grouping in groupings
    }

    # Now that we have the choices, generate MultipleChoiceFields with them
    fields = {
        grouping.title: forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple,
            choices=choices[grouping]
        ) for grouping in groupings
    }

    # now generate the form
    form = forms.Form()
    form.fields.update(fields)

    return form


def event_grouping_form_validates(calendar_id, form):
    # todo
    return True
