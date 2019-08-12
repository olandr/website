import os

from django import template
from django.utils import timezone

from app import settings
from event.enums import ApplicationStatus

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def time_left(time: timezone.datetime):
    return time - timezone.now()


@register.filter
def days_left(timedelta: timezone.timedelta):
    return int(timedelta.total_seconds() // (60*60*24))


@register.filter
def days_left(timedelta: timezone.timedelta):
    return int(timedelta.total_seconds() // (60*60*24))


@register.filter
def file_name(value):
    return os.path.basename(value.file.name)


@register.filter
def display_departments(departments):
    return " / ".join([d.name for d in departments])
