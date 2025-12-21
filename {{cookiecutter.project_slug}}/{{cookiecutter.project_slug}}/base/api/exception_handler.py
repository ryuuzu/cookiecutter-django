import math

from django.utils.encoding import force_str
from django.utils.translation import ngettext
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler

from {{ cookiecutter.project_slug }}.base.api.serializers import ResponseSerializer
from {{ cookiecutter.project_slug }}.base.exceptions import BaseException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exception, BaseException):
        return Response(
            ResponseSerializer(
                {
                    "status": "error",
                    "code": exception.code,
                    "title": exception.title,
                    "detail": exception.detail,
                }
            ).data,
            status=exception.status_code,
        )
    if isinstance(exc, Throttled):
        default_detail = "Too many attempts."
        extra_detail_singular = "Please try again after {wait} second."
        extra_detail_plural = "Please try again after {wait} seconds."

        if exc.wait is not None:
            wait = math.ceil(exc.wait)
            detail = " ".join(
                (
                    default_detail,
                    force_str(
                        ngettext(
                            extra_detail_singular.format(wait=wait),
                            extra_detail_plural.format(wait=wait),
                            wait,
                        ),
                    ),
                ),
            )
        else:
            detail = default_detail

        return Response(
            {"detail": detail}, status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return response
