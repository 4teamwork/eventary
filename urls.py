from django.conf.urls import url

from . import views

app_name = 'cal'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(
        r'^cal_(?P<calendar_id>[0-9]*)/event_(?P<event_id>[0-9]*)/$',
        views.details,
        name='details'
    ),
]
