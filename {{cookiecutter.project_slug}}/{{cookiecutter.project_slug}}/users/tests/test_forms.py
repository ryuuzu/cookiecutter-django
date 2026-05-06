"""Module for all form tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from {{ cookiecutter.project_slug }}.users.forms import UserAdminCreationForm

if TYPE_CHECKING:
    from {{ cookiecutter.project_slug }}.users.models import User


class TestUserAdminCreationForm:
    """Tests for the admin user creation form."""

    def test_username_validation_error_msg(self, user: User):
        """Tests that the form rejects duplicate identifiers."""

        form = UserAdminCreationForm(
            {
                {%- if cookiecutter.username_type == "email" %}
                "email": user.email,
                {%- else %}
                "username": user.username,
                {%- endif %}
                "password1": "My_R@ndom-P@ssw0rd",
                "password2": "My_R@ndom-P@ssw0rd",
            },
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        {%- if cookiecutter.username_type == "email" %}
        assert "email" in form.errors
        {%- else %}
        assert "username" in form.errors
        {%- endif %}
