from django.contrib.auth.models import User as DjangoUser
from django.db import models


class Calendar(models.Model):
    # To allow several calendars in the same application,
    # a calendar model is generated, to which the events
    # are related enabling event discrimination by calendar
    title = models.CharField(max_length=255)


class Host(DjangoUser):
    # The host contains all the information about the host.
    # The attributes of the DjangoUser are:
    #   username, password, email, first_name, last_name
    # For our purpose we need further fields
    organization = models.CharField('hosting organization', max_length=50)
    phone = models.CharField(max_length=20)
    homepage = models.URLField()


class Event(models.Model):
    # The event model contains all the information related
    # to an event. Since date and time information requires
    # some flexibility its split up into a custom model and
    # linked to the event through a one to many relation.
    calendar = models.ForeignKey(Calendar)
    image = models.ImageField()
    document = models.FileField()
    host = models.ForeignKey(Host)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    homepage = models.URLField()
    published = models.BooleanField('publication status')
    description = models.TextField('description')
    comment = models.CharField('comment', max_length=255)
    prize = models.DecimalField('prize', max_digits=6, decimal_places=2)


class EventTimeDate(models.Model):
    # Each event can take place at several times / dates.
    # This model allows to assign times / dates to an event
    event = models.ForeignKey(Event)
    start_date = models.DateField('start date')
    start_time = models.TimeField('start time')
    end_date = models.DateField('end date')
    end_time = models.TimeField('end time')
    comment = models.CharField('comment', max_length=255)
    prize = models.DecimalField('prize', max_digits=6, decimal_places=2)
