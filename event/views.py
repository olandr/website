import math
import datetime
import os

import pytz
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from app.utils import login_verified_required
from app.variables import HACKATHON_TIMEZONE
from app.views import response
from event.enums import DietType, TshirtSize, ApplicationStatus, SubscriberStatus
from event.models import Application, Subscriber
from event.utils import get_event, get_application, get_applications
from user.utils import is_participant, is_organiser


@login_verified_required
@user_passes_test(is_participant)
def apply(request, code):
    current_data = dict()
    current_event = get_event(code=code)
    if current_event:
        current_data["event"] = current_event
        current_data["years"] = [
            (timezone.now().year + year, year == 0) for year in range(-1, 5)
        ]
        current_data["diets"] = [
            (diet.name.capitalize().replace("_", " "), diet.value) for diet in DietType
        ]
        current_data["tshirts"] = [
            (tshirt.name.upper(), tshirt.value) for tshirt in TshirtSize
        ]
        current_application = get_application(
            event_id=current_event.id, user_id=request.user.id
        )
        current_data["status"] = "DRAFT"
        if current_application:
            current_data["application"] = current_application
            current_data["tshirt_int"] = int(current_application.tshirt)
            if current_application.status in [
                ApplicationStatus.DRAFT.value,
                ApplicationStatus.PENDING.value,
                ApplicationStatus.CANCELLED.value,
                ApplicationStatus.INVITED.value,
                ApplicationStatus.CONFIRMED.value,
                ApplicationStatus.ATTENDED.value,
            ]:
                current_data["status"] = ApplicationStatus(
                    current_application.status
                ).name.upper()
            else:
                current_data["status"] = "PENDING"
        if (
            request.method == "POST"
            and not current_application
            or (
                current_application
                and current_application.status == ApplicationStatus.DRAFT.value
            )
        ):
            required_fields = [
                "university",
                "degree",
                "graduation_year",
                "description",
                "projects",
                "diet",
                "tshirt",
            ]
            all_filled = True
            for required_field in required_fields:
                if (
                    required_field not in request.POST
                    or not request.POST[required_field]
                ):
                    all_filled = False
            all_filled &= "resume" in request.FILES if not current_application else True
            if all_filled:
                # TODO: Display messages of error and validate URLs
                university = request.POST["university"]
                degree = request.POST["degree"]
                graduation_year = request.POST["graduation_year"]
                description = request.POST["description"]
                projects = request.POST["projects"]
                github = request.POST["github"] if "github" in request.POST else ""
                devpost = request.POST["devpost"] if "devpost" in request.POST else ""
                linkedin = (
                    request.POST["linkedin"] if "linkedin" in request.POST else ""
                )
                website = request.POST["website"] if "website" in request.POST else ""
                resume = request.FILES["resume"] if "resume" in request.FILES else None
                resume_available = (
                    request.POST["resume_available"] == "on"
                    if "resume_available" in request.POST
                    else False
                )
                diet = request.POST["diet"]
                diet_other = (
                    request.POST["diet_other"] if "diet_other" in request.POST else ""
                )
                tshirt = request.POST["tshirt"]
                hardware = (
                    request.POST["hardware"] if "hardware" in request.POST else ""
                )
                status = (
                    ApplicationStatus.PENDING.value
                    if request.POST["submit"] == "apply"
                    else ApplicationStatus.DRAFT.value
                )
                if current_application:
                    application = current_application
                    application.description = description
                    application.projects = projects
                    if resume:
                        application.resume.delete()
                        application.resume = resume
                    application.resume_available = resume_available
                    application.university = university
                    application.degree = degree
                    application.graduation_year = graduation_year
                    application.github = github
                    application.devpost = devpost
                    application.linkedin = linkedin
                    application.website = website
                    application.diet = diet
                    application.diet_other = diet_other
                    application.tshirt = tshirt
                    application.hardware = hardware
                    application.status = status
                else:
                    application = Application(
                        event_id=current_event.id,
                        user_id=request.user.id,
                        description=description,
                        projects=projects,
                        resume=resume,
                        resume_available=resume_available,
                        university=university,
                        degree=degree,
                        graduation_year=graduation_year,
                        github=github,
                        devpost=devpost,
                        linkedin=linkedin,
                        website=website,
                        diet=diet,
                        diet_other=diet_other,
                        tshirt=tshirt,
                        hardware=hardware,
                        status=status,
                    )
                application.save()
                return HttpResponseRedirect("")
        return render(request, "apply.html", current_data)
    return HttpResponseNotFound()


@login_verified_required
@user_passes_test(is_organiser)
def applications(request, code):
    current_data = dict()
    current_event = get_event(code=code)
    if current_event:
        current_data["event"] = current_event
        current_data["applications"] = get_applications(event_id=current_event.id)
        return render(request, "applications.html", current_data)
    return HttpResponseNotFound()


def subscribe(request, id):
    subscriber = Subscriber.objects.filter(
        id=id,
        status__in=[
            SubscriberStatus.PENDING.value,
            SubscriberStatus.UNSUBSCRIBED.value,
        ],
    ).first()
    if subscriber:
        subscriber.status = SubscriberStatus.SUBSCRIBED.value
        subscriber.save()
        messages.add_message(request, messages.INFO, "Your email has been verified!")
    else:
        subscriber = Subscriber.objects.filter(
            id=id, status=SubscriberStatus.SUBSCRIBED.value
        ).first()
        if subscriber:
            messages.add_message(
                request, messages.INFO, "Your email has already been verified before!"
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "We are sorry, but we couldn't verify your email!",
            )
    return HttpResponseRedirect(reverse("app_home"))


def unsubscribe(request, id):
    subscriber = Subscriber.objects.filter(
        id=id, status=SubscriberStatus.SUBSCRIBED.value
    ).first()
    if subscriber:
        subscriber.status = SubscriberStatus.UNSUBSCRIBED.value
        subscriber.save()
        messages.add_message(request, messages.INFO, "You have been unsubscribed!")
    else:
        messages.add_message(
            request, messages.ERROR, "We are sorry, but we couldn't verify your email!"
        )
    return HttpResponseRedirect(reverse("app_home"))


def live(request, code):
    current_data = dict()
    current_event = get_event(code=code, application_status=None)
    if current_event:
        current_data["event"] = current_event
        if current_event.schedule:
            current_line = 0
            schedule = list()
            current_day = None
            current_starts_at = None
            current_ends_at = None
            current_title = None
            for schedule_line in current_event.schedule.replace("\r", "").split("\n"):
                if schedule_line:
                    try:
                        current_day = datetime.datetime.strptime(
                            schedule_line[1:].lstrip(), "%Y-%m-%d"
                        )
                    except ValueError:
                        pass
                    try:
                        if not current_starts_at:
                            current_starts_at = datetime.datetime.strptime(
                                schedule_line, "%H:%M"
                            )
                        else:
                            current_ends_at = datetime.datetime.strptime(
                                schedule_line, "%H:%M"
                            )
                    except ValueError:
                        pass
                    if schedule_line[:2] == "##":
                        current_title = schedule_line[2:].lstrip()
                    elif schedule_line[0] == ">":
                        current_description = schedule_line[1:].lstrip()
                        if current_title and current_starts_at:
                            schedule_item = dict(
                                name=current_title,
                                description=current_description,
                                starts_at=timezone.datetime(
                                    day=current_day.day,
                                    month=current_day.month,
                                    year=current_day.year,
                                    hour=current_starts_at.hour,
                                    minute=current_starts_at.minute,
                                    tzinfo=None,
                                ),
                            )
                            if current_ends_at:
                                schedule_item["ends_at"] = timezone.datetime(
                                    day=current_day.day,
                                    month=current_day.month,
                                    year=current_day.year,
                                    hour=current_ends_at.hour,
                                    minute=current_ends_at.minute,
                                    tzinfo=None,
                                )
                            list.append(schedule, schedule_item)
                            current_title = None
                            current_starts_at = None
                            current_ends_at = None
                        else:
                            return response(
                                request,
                                code=500,
                                message="The schedule file for the event is wrongly formatted on line "
                                + str(current_line)
                                + ".",
                            )
                    current_line += 1
        else:
            return response(request, code=404)
        starts_at = current_event.starts_at.replace(minute=0, second=0).replace(
            tzinfo=None
        )
        ends_at = current_event.ends_at
        if ends_at.minute > 0 or ends_at.second > 0:
            ends_at += timezone.timedelta(hours=1)
        ends_at = ends_at.replace(minute=0, second=0).replace(tzinfo=None)
        hours = [
            (
                # TODO: Fix timezone
                starts_at + timezone.timedelta(hours=h + 2),
                starts_at + timezone.timedelta(hours=h + 3),
            )
            for h in range(math.ceil((ends_at - starts_at).total_seconds() / 3600.0))
        ]
        current_data["schedule"] = [
            dict(
                time_from=hour[0].replace(tzinfo=None),
                time_to=hour[1].replace(tzinfo=None),
                schedule=[
                    schedule_item
                    for schedule_item in schedule
                    if hour[0]
                    # TODO: Fix timezone
                    <= schedule_item["starts_at"] < hour[1]
                ],
            )
            for hour in hours
        ]
        days = []
        for hour in hours:
            if hour[0].date() not in [d.date() for d in days]:
                list.append(days, hour[0].replace(tzinfo=None))
        current_data["days"] = days
        # TODO: Fix timezone
        now = timezone.now()
        if now > current_event.ends_at:
            now = current_event.ends_at
        current_data["now"] = now
        current_data["now_tz"] = now.replace(tzinfo=None) + timezone.timedelta(hours=2)
        return render(request, "live.html", current_data)
    return response(request, code=404)
