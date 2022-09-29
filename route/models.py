from django.db import models
from django.utils.translation import gettext_lazy

# Create your models here.


class Place(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting = models.IntegerField()
    stopping = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()

    class RouteType(models.TextChoices):
        car = 'Car', gettext_lazy('Car')
        bicycle = 'Bicycle', gettext_lazy('Bicycle')

    route_type = models.CharField(max_length=50, choices=RouteType.choices,
                                  default=RouteType.car)
    duration = models.IntegerField()


class Event(models.Model):
    route_id = models.IntegerField()
    event_admin = models.IntegerField()
    approved_user = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()
