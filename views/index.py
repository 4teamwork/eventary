from datetime import datetime

from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, RedirectView

from ..forms import GenericFilterForm
from ..models import Calendar, Event, EventTimeDate


class UserRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        admins = Group.objects.get(name='eventary_admins')
        redactors = Group.objects.get(name='eventary_redactors')
        
        if redactors in self.request.user.groups.all():
            return reverse('eventary:redactors-landing')
        elif admins in self.request.user.groups.all():
            return reverse('eventary:admins-landing')
        else:
            return reverse('eventary:users-landing')
