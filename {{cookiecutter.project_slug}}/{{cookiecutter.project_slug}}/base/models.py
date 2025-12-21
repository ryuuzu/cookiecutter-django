from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from {{ cookiecutter.project_slug }}.base.managers import BaseManager


class BaseModel(models.Model):
    """
    Base model for all models in the project.
    """
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created_by",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_%(app_label)s_%(class)s",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="deleted_%(app_label)s_%(class)s",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    locked = models.BooleanField(default=False)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adding these in case of direct object creation. For e.g. bulk_create
        datetime_now = timezone.now()
        if not self.created_at:
            self.created_at = datetime_now
        if not self.updated_at:
            self.updated_at = datetime_now

    def _add_to_update_fields(self, update_fields, field_name):
        """
        Helper method to add a field to the update_fields list if it exists.
        """
        if field_name not in update_fields:
            update_fields = list(update_fields)
            update_fields.append(field_name)
        return update_fields

    def save(self, *args, **kwargs):
        datetime_now = timezone.now()
        if not self.id:
            self.created_at = datetime_now

            if kwargs.get("update_fields"):
                kwargs["update_fields"] = self._add_to_update_fields(
                    kwargs["update_fields"],
                    "created_at",
                )
        self.updated_at = datetime_now

        if kwargs.get("update_fields"):
            kwargs["update_fields"] = self._add_to_update_fields(
                kwargs["update_fields"],
                "updated_at",
            )

        # ruff: noqa: DJ012
        return super().save(*args, **kwargs)

    def restore(self, *args, **kwargs):
        self.is_deleted = False
        self.save(
            *args,
            **kwargs,
            update_fields=["is_deleted"],
        )

    def delete(self, *args, **kwargs):
        if self.locked:
            msg = "Cannot delete a locked object."
            raise ValueError(msg)

        deleted_by = kwargs.pop("deleted_by", None)

        self.deleted_by = deleted_by
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(
            *args,
            **kwargs,
            update_fields=["deleted_at", "is_deleted", "deleted_by"],
        )

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    @classmethod
    def get_validation_sql_logic(
        cls,
        field_name,
        field_value,
        pk=None,
    ):
        sql_logic = models.Q(**{field_name: field_value})

        if pk:
            sql_logic &= ~models.Q(pk=pk)

        return sql_logic

    @classmethod
    def validate_field_as_unique(
        cls,
        field_name,
        field_value,
        pk=None,
    ):
        if cls.objects.filter(
            cls.get_validation_sql_logic(
                field_name,
                field_value,
                pk,
            ),
        ).exists():
            msg = f"{field_value} already exists."
            raise ValueError(msg)

    @classmethod
    def validate_field_as_unique_including_deleted(
        cls,
        field_name,
        field_value,
        pk=None,
    ):
        sql_logic = cls.get_validation_sql_logic(
            field_name,
            field_value,
            pk,
        )

        if cls.objects.filter(sql_logic).exists():
            msg = f"{field_value} already exists."
            raise ValueError(msg)

        if cls.objects.all_objects().filter(sql_logic).exists():
            msg = f"{field_value} already exists in trash. Please restore and use it."
            raise ValueError(msg)
