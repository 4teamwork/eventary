from django.core.urlresolvers import reverse
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from ..forms import CalendarForm, FilterForm
from ..models import Calendar


class CalendarListView(ListView):

    model = Calendar
    template_name = 'eventary/calendars/list.html'


class CalendarCreateView(CreateView):

    form_class = CalendarForm
    model = Calendar
    template_name = 'eventary/calendars/create.html'

    def get_success_url(self):
        """Returns the user to the details view of the created calendar."""

        return reverse(
            'eventary:calendar_details',
            args=[self.object.pk]
        )


class CalendarDetailView(FormMixin, SingleObjectMixin, ListView):

    form_class = FilterForm
    model = Calendar
    template_name = 'eventary/calendars/details.html'

    def filter_qs(self, qs):
        form = self.get_form()
        if form.is_valid():
            data = form.clean()
            # filter by date
            if data['from_date'] is not None:
                qs = qs.exclude(
                    eventtimedate__start_date__lt=data['from_date']
                )
            if data['to_date'] is not None:
                qs = qs.exclude(
                    eventtimedate__end_date__gt=data['to_date']
                )
            # filter by the selected groups
            groups = form.groups()
            if len(groups) > 0:
                qs = qs.filter(group__in=groups)
        return qs.distinct()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Calendar.objects.all())
        return super(CalendarDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CalendarDetailView, self).get_context_data(**kwargs)
        context['calendar'] = self.object

        # filter the list of events with the form data
        object_qs = self.get_queryset()
        object_qs = self.filter_qs(object_qs)

        # paginate the querysets
        paginator, page, object_list, is_paginated = self.paginate_queryset(
            object_qs,
            25
        )

        # update the context
        context.update({
            'paginator': paginator,
            'page': page,
            'object_list': object_list,
            'event_list': object_list
        })

        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs(), calendar=self.object)

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial()}
        if len(self.request.GET):
            kwargs.update({
                'data': self.request.GET
            })
        return kwargs

    def get_queryset(self):
        return self.object.event_set.filter(published=True)


class CalendarUpdateView(UpdateView):

    form_class = CalendarForm
    model = Calendar
    template_name = 'eventary/calendars/update.html'
