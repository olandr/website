import re
from typing import List

import html2text as html2text
from django.conf import settings
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.defaultfilters import first
from django.urls import reverse

from app.variables import (
    HACKATHON_ORGANIZER_EMAIL_REGEX,
    HACKATHON_EMAIL_PREFIX,
    HACKATHON_EMAIL_NOREPLY,
    HACKATHON_EMAIL_CONTACT,
    HACKATHON_NAME,
)
from user.enums import DepartmentType


def get_substitutions_templates():
    return {
        "hk_app_name": getattr(settings, "HACKATHON_APP_NAME", None),
        "hk_name": getattr(settings, "HACKATHON_NAME", None),
        "hk_description": getattr(settings, "HACKATHON_DESCRIPTION", None),
        "hk_timezone": getattr(settings, "HACKATHON_TIMEZONE", None),
        "hk_domain": getattr(settings, "HACKATHON_DOMAIN", None),
        "hk_email_contact": getattr(settings, "HACKATHON_EMAIL_CONTACT", None),
        "hk_email_webdev": getattr(settings, "HACKATHON_EMAIL_WEBDEV", None),
        "hk_email_sponsorship": getattr(settings, "HACKATHON_EMAIL_SPONSORSHIP", None),
        "hk_sn_facebook": getattr(settings, "HACKATHON_SN_FACEBOOK", None),
        "hk_sn_twitter": getattr(settings, "HACKATHON_SN_TWITTER", None),
        "hk_sn_instagram": getattr(settings, "HACKATHON_SN_INSTAGRAM", None),
        "hk_sn_youtube": getattr(settings, "HACKATHON_SN_YOUTUBE", None),
        "hk_sn_linkedin": getattr(settings, "HACKATHON_SN_LINKEDIN", None),
        "hk_sn_medium": getattr(settings, "HACKATHON_SN_MEDIUM", None),
        "hk_sn_github": getattr(settings, "HACKATHON_SN_GITHUB", None),
    }


def variables_processor(request):
    c = get_substitutions_templates()
    from event.utils import get_next_or_past_event

    event = get_next_or_past_event()
    if event:
        c["event"] = event
        c["background_video"] = event.background.name[-4:] == ".mp4"
        c["background_image"] = event.background.name[-4:] in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
        ]
    return c


def is_email_organizer(email):
    return re.match(HACKATHON_ORGANIZER_EMAIL_REGEX, email)


def get_notification_template(type: str, method: str, task: str, format: str):
    return settings.NOTIFY_TEMPLATES[method][type][task][format]


def send_email(
    subject,
    body,
    to,
    from_email=None,
    reply_to=None,
    tags=None,
    track_clicks=False,
    fail_silently=False,
    attachments=None,
):
    if tags is None:
        tags = []

    tags += HACKATHON_NAME.lower()

    if to and not isinstance(to, (list, tuple)):
        to = [to]

    if reply_to and not isinstance(reply_to, (list, tuple)):
        reply_to = [reply_to]

    body_plain = html2text.html2text(body)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_plain,
        from_email=from_email or HACKATHON_NAME + "<" + HACKATHON_EMAIL_NOREPLY + ">",
        to=to,
        reply_to=reply_to or [HACKATHON_NAME + "<" + HACKATHON_EMAIL_CONTACT + ">"],
        attachments=attachments,
    )

    msg.attach_alternative(body, "text/html")

    if tags:
        msg.tags = tags

    msg.track_clicks = track_clicks

    return msg.send(fail_silently=fail_silently)


def login_verified_required(function):
    def wrapper(request, *args, **kw):
        if request.user.id:
            if request.user.is_active and request.user.email_verified:
                return function(request, *args, **kw)
            else:
                return HttpResponseRedirect(reverse("user_verify"))
        else:
            return HttpResponseRedirect(reverse("user_login"))

    return wrapper


def require_department(departments: List[DepartmentType], **decokwargs):
    def _funcwrap(view_func):
        def _argwrap(*args, **kwargs):
            request = first(
                [
                    a
                    for a in list(args) + list(kwargs.values())
                    if isinstance(a, WSGIRequest)
                ]
            )

            if not departments:
                raise Exception("Provide at least one department to require it.")

            if not request:
                raise Exception(
                    "One of the arguments of decorated function must be a WSGIRequest instance."
                )

            if not request.user:
                messages.error(request, "You need to be logged in!")
                return redirect(request.path)

            if (
                request.user.is_admin
                or request.user.is_director
                or any(
                    [
                        department.value
                        in request.user.departments.all().values_list("type", flat=True)
                        for department in departments
                    ]
                )
            ):
                return view_func(*args, **kwargs)

            messages.error(
                request, "You don't have enough permissions to do this action."
            )
            return redirect(reverse("admin:index"))

        return _argwrap

    return _funcwrap
