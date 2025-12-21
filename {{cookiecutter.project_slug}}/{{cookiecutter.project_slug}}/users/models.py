{%- if cookiecutter.username_type == "email" %}
from typing import ClassVar

{% endif -%}
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db import models
{%- if cookiecutter.username_type == "email" %}
from django.db.models import EmailField
{%- endif %}
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
{%- if cookiecutter.username_type == "email" %}

from .managers import UserManager
{%- endif %}

class PasswordHistory(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="past_passwords"
    )
    password = models.CharField(_("password"), max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    """
    Default custom user model for {{cookiecutter.project_name}}.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    class GenderChoices(models.TextChoices):
        choices: list[tuple[str, str]]

        MALE = "male", _("Male")
        FEMALE = "female", _("Female")
        OTHER = "other", _("Other")
        PREFER_NOT_TO_SAY = "prefer_not_to_say", _("Prefer not to say")


    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    {%- if cookiecutter.username_type == "email" %}
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()
    {%- endif %}
    gender = models.CharField(
        max_length=50, choices=GenderChoices.choices, default=GenderChoices.PREFER_NOT_TO_SAY
    )

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created_by",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="updated_%(app_label)s_%(class)s",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="deleted_%(app_label)s_%(class)s",
        null=True,
        blank=True,
    )
    color = models.CharField(max_length=7, default=get_random_color_code)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)



    @property
    def can_be_reinvited(self) -> bool:
        return not self.is_active and not self.has_usable_password()

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
        super().save(*args, **kwargs)

    def restore(self, *args, **kwargs):
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save(
            *args,
            **kwargs,
            update_fields=["is_deleted", "deleted_at", "is_active"],
        )

    def delete(self, *args, **kwargs):
        deleted_by = kwargs.pop("deleted_by", None)

        self.deleted_by = deleted_by
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.is_active = False
        self.save(
            *args,
            **kwargs,
            update_fields=["deleted_at", "is_deleted", "deleted_by", "is_active"],
        )

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def check_against_past_passwords(self, password: str) -> bool:
        """Check if the password is not in the past passwords.

        Args:
            password (str): Password to check.

        Returns:
            bool: True if password is not in the past passwords.

        """
        return not any(
            check_password(password, past_password.password)
            for past_password in self.past_passwords.order_by("-created_at")[:3]
        )

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        {%- if cookiecutter.username_type == "email" %}
        return reverse("users:detail", kwargs={"pk": self.id})
        {%- else %}
        return reverse("users:detail", kwargs={"username": self.username})
        {%- endif %}
