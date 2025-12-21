from django.contrib.auth.models import Group
from django_filters import rest_framework as filters

from {{ cookiecutter.project_slug }}.users.models import User


class UserFilter(filters.FilterSet):
    groups = filters.ModelMultipleChoiceFilter(
        field_name="groups", queryset=Group.objects.all(), label="Role (Group)"
    )

    class Meta:
        model = User
        fields = ("groups", )
