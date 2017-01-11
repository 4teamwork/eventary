from django.contrib.auth.models import User as DjangoUser
from django.db import models

from autoslug import AutoSlugField


class Calendar(models.Model):
    # To allow several calendars in the same application,
    # a calendar model is generated, to which the events
    # are related enabling event discrimination by calendar
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title')

    def __str__(self):
        return self.title


class Host(DjangoUser):
    # The host contains all the information about the host.
    # The attributes of the DjangoUser are:
    #   username, password, email, first_name, last_name
    # For our purpose we need further fields
    organization = models.CharField('hosting organization', max_length=50)
    phone = models.CharField(max_length=20)
    homepage = models.URLField()

    def __str__(self):
        return "{0} {1} [{2}]".format(
            self.first_name,
            self.last_name,
            self.organization
        )


class Event(models.Model):
    # The event model contains all the information related
    # to an event. Since date and time information requires
    # some flexibility its split up into a custom model and
    # linked to the event through a one to many relation.
    calendar = models.ForeignKey(Calendar)
    image = models.ImageField(
        upload_to='cal/images/%Y/%m/%d',
        null=True,
        blank=True
    )
    document = models.FileField(
        upload_to='cal/documents/%Y/%m/%d',
        null=True,
        blank=True
    )
    host = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    published = models.BooleanField('publication status')
    description = models.TextField('description', null=True, blank=True)
    proposed = models.DateField(auto_now_add=True)
    comment = models.CharField(
        'comment',
        max_length=255,
        null=True,
        blank=True
    )
    prize = models.DecimalField(
        'prize',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return "{0} @ {1} by {2}".format(self.title, self.location, self.host)


class EventTimeDate(models.Model):
    # Each event can take place at several times / dates.
    # This model allows to assign times / dates to an event
    event = models.ForeignKey(Event)
    start_date = models.DateField('start date')
    start_time = models.TimeField('start time')
    end_date = models.DateField('end date')
    end_time = models.TimeField('end time')
    comment = models.CharField(
        'comment',
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return "{0} - {1} > {2}".format(
            self.event.title,
            self.start_date,
            self.end_date
        )


class Grouping(models.Model):
    title = models.CharField(max_length=255)
    calendars = models.ManyToManyField('Calendar', blank=True, null=True)

    def __str__(self):
        return "{0} -- {1}".format(
            self.title,
            ", ".join([c.title for c in self.calendars.all()])
        )


class Group(models.Model):
    title = models.CharField(max_length=255)
    grouping = models.ForeignKey(Grouping)
    events = models.ManyToManyField('Event', null=True, blank=True)

    def __str__(self):
        return "{0} -- {1}".format(self.title, self.grouping.title)
