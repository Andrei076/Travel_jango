from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy
import json


def validate_stopping_point(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('error')
    except:
        raise ValidationError('Form is not json')


def validate_route_type(value):
    if value.title() not in ['Car', 'Bicycle']:
        raise ValidationError('error')


def validate_date(value):
    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
    except:
        raise ValidationError('error')
    if datetime.today() > parsed_date:
        raise ValidationError('error')


class Place(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting = models.IntegerField()
    stopping = models.CharField(max_length=50)
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()

    class RouteType(models.TextChoices):
        car = 'Car', gettext_lazy('Car')
        bicycle = 'Bicycle', gettext_lazy('Bicycle')

    route_type = models.CharField(max_length=50, choices=RouteType.choices,
                                  default=RouteType.car,  validators=[validate_route_type])
    duration = models.IntegerField()


class Event(models.Model):
    route_id = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=50, null=True)
    start_date = models.DateField(validators=[validate_date])
    price = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()


