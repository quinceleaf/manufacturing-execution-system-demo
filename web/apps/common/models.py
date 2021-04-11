from django.db import models
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

import csv

# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from simple_history.models import HistoricalRecords
import ulid


# ––– MODELS


def generate_ulid():
    return str(ulid.ULID())


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class HistoryMixin(models.Model):
    history = HistoricalRecords(inherit=True)

    def get_history(self):
        return_data = []
        all_histories = self.history.all()
        for history in all_histories:
            delta = history.diff_against(history.prev_record)
            for change in delta.changes:
                if change.old:
                    comment = (
                        f"{change.field} changed from {change.old} to {change.new}"
                    )
                else:
                    comment = f"{change.field} set to {change.new}"
            return_data.append(
                {
                    "date": history.history_date,
                    "user": history.history_user,
                    "comment": comment,
                }
            )
        return return_data

    class Meta:
        abstract = True


class AbstractBaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        unique=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    def get_fields(self):
        return [
            (field.name, field.value_to_string(self))
            for field in self.__class__._meta.fields
        ]

    class Meta:
        abstract = True


class ImmutableBaseModel(models.Model):

    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        unique=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    def get_fields(self):
        return [
            (field.name, field.value_to_string(self))
            for field in self.__class__._meta.fields
        ]

    class Meta:
        abstract = True


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(AbstractBaseModel):
    def __str__(self):
        return f"Common app settings"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PLACEHOLDER
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Placeholder(AbstractBaseModel):

    CHOICES = [
        (1, "Choice 1"),
        (2, "Choice 2"),
    ]

    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TAG
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Tag(AbstractBaseModel):
    name = models.CharField("Tag", max_length=24, null=True)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("core:tag_detail", kwargs={"pk": self.id})

    class Meta:
        ordering = ["name"]
