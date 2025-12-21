from rest_framework.request import Request

from {{ cookiecutter.project_slug }}.users.models import User


class BaseRequest(Request):
    user: User
