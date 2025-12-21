from django.conf import settings
from django.shortcuts import redirect
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class MiddlewareResponseRendererMixin:
    def _get_response(self, response: Response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response
