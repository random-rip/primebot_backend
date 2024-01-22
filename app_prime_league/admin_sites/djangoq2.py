from django.contrib import admin
from django_q.admin import FailAdmin as DjangoQ2FailAdmin
from django_q.admin import ScheduleAdmin as DjangoQ2ScheduleAdmin
from django_q.admin import TaskAdmin as DjangoQ2TaskAdmin
from django_q.models import Failure, Schedule, Success

admin.site.unregister(Schedule)
admin.site.unregister(Failure)
admin.site.unregister(Success)


class ScheduleAdmin(DjangoQ2ScheduleAdmin):
    list_display = (
        "id",
        "name",
        "schedule_type",
        "repeats",
        "cluster",
        "next_run",
        "get_last_run",
        "get_success",
    )


class TaskAdmin(DjangoQ2TaskAdmin):
    list_display = (
        "name",
        "group",
        "cluster",
        "started",
        "stopped",
        "time_taken",
    )


class FailAdmin(DjangoQ2FailAdmin):
    list_display = (
        "name",
        "group",
        "cluster",
        "started",
        "stopped",
        "short_result",
    )
