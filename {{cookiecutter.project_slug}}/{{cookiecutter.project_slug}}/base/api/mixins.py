import logging
from collections.abc import Callable, Iterable
from typing import Generic, TypeVar

from django.core.cache import cache
from django.db.models import Prefetch, QuerySet
from django_filters import FilterSet
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from {{ cookiecutter.project_slug }}.base.api.permissions import (
    AdminGroupOnlyPermission,
    ReadOnlyPermission,
)
from {{ cookiecutter.project_slug }}.base.api.request import BaseRequest
from {{ cookiecutter.project_slug }}.base.api.serializers import (
    BaseModelSerializer,
    EmptySerializer,
    ResponseSerializer,
)
from {{ cookiecutter.project_slug }}.base.exceptions import BadRequest, Forbidden
from {{ cookiecutter.project_slug }}.base.models import BaseModel
from {{ cookiecutter.project_slug }}.users.utils import get_user_prefetch_data

_ModelT = TypeVar("_ModelT", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseModelViewSetMixin(Generic[_ModelT]):
    allow_view_deleted = True
    disable_pagination = True
    queryset: QuerySet
    request: BaseRequest
    model: _ModelT
    filterset_class: FilterSet
    search_fields: Iterable[str] = []
    serializer_class = BaseModelSerializer
    select_related: Iterable[str] = ["created_by", "updated_by", "deleted_by"]
    prefetch_related: Iterable[str | Prefetch] = []

    get_serializer: Callable[..., BaseModelSerializer]
    get_object: Callable[..., _ModelT]
    filter_queryset: Callable[..., QuerySet[_ModelT]]
    get_serializer_context: Callable[..., dict]

    def get_serializer_context(self):
        """
        This method is overridden to add id of the object in case of detail view.
        It is used by `UniqueFieldValidator` to validate uniqueness of fields.

        Utsav: My dumbass removed this once and validator stopped working and I
        was confused why it was not working bhanera :)
        """
        context = super().get_serializer_context()  # type: ignore

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field  # type: ignore

        context.update({self.lookup_field: self.kwargs.get(lookup_url_kwarg)})  # type: ignore

        return context

    def get_queryset(self):
        if self.request.user.is_superuser and self.allow_view_deleted:
            try:
                queryset = self.model.objects.all_objects()
            except AttributeError:
                queryset = self.model.objects.all()
        else:
            queryset = self.model.objects.all()

        return (
            queryset
            .select_related(*self.select_related)
            .prefetch_related(*self.prefetch_related)
        )

    def perform_destroy(self, instance):
        return instance.delete(deleted_by=self.request.user)

    def list(self, request, *args, **kwargs):
        if self.disable_pagination:
            queryset = self.filter_queryset(self.get_queryset())

            serializer = self.get_serializer(
                queryset,
                many=True,
                context=self.get_serializer_context(),
            )
            return Response({"count": queryset.count(), "results": serializer.data})
        else:
            return super().list(request, *args, **kwargs)

    @extend_schema(
        request=EmptySerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="deleted",
        url_name="deleted",
        permission_classes=[AdminGroupOnlyPermission],
    )
    def deleted(self, request, *args, **kwargs):
        """
        List all deleted objects.
        """
        if not self.allow_view_deleted:
            raise Forbidden(
                "Viewing deleted objects is not allowed for this model.",
                "View Deleted Not Allowed",
            )

        queryset = self.get_queryset().filter(is_deleted=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=EmptySerializer,
        responses=ResponseSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
        url_name="restore",
        permission_classes=[AdminGroupOnlyPermission],
    )
    def restore(self, request, *args, **kwargs):
        if not self.allow_view_deleted:
            raise Forbidden(
                "Restoring deleted objects is not allowed for this model.",
                "Restore Not Allowed",
            )

        instance = self.get_object()

        if not instance.is_deleted:
            raise BadRequest(
                "Object is not deleted.",
                "Object Not Deleted",
            )

        instance.restore()
        return Response(
            ResponseSerializer(
                {
                    "detail": "Object restored successfully.",
                },
            ).data,
            status=200,
        )

    @extend_schema(
        request=EmptySerializer,
        responses=ResponseSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="delete-permanently",
        url_name="delete_permanently",
        permission_classes=[AdminGroupOnlyPermission],
    )
    def delete_permanently(self, request, *args, **kwargs):
        if not self.allow_view_deleted:
            raise Forbidden(
                "Permanently deleting objects is not allowed for this model.",
                "Permanent Delete Not Allowed",
            )

        instance = self.get_object()

        if not instance.is_deleted:
            raise BadRequest(
                "Object is not deleted.",
                "Object Not Deleted",
            )

        instance.hard_delete()
        return Response(
            ResponseSerializer(
                {
                    "detail": "Object deleted permanently successfully.",
                },
            ).data,
            status=200,
        )

    @extend_schema(
        request=EmptySerializer,
        responses=ResponseSerializer,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="empty-trash",
        url_name="empty_trash",
        permission_classes=[AdminGroupOnlyPermission],
    )
    def empty_trash(self, request, *args, **kwargs):
        if not self.allow_view_deleted:
            raise Forbidden(
                "Emptying trash is not allowed for this model.",
                "Empty Trash Not Allowed",
            )

        logger.info(
            "Emptying trash for model: %s by user: %s",
            self.model.__name__,
            request.user.email,
        )
        cache.set(
            f"skip_log_report_activity:{request.user.id}",
            True,
            timeout=60,
        )  # 60 seconds timeout

        try:
            self.model.objects.all_objects().filter(is_deleted=True).delete()
            logger.info(
                "Trash emptied for model: %s by user: %s",
                self.model.__name__,
                request.user.email,
            )
        finally:
            cache.delete(f"skip_log_report_activity{request.user.id}")

        return Response(
            ResponseSerializer(
                {
                    "detail": "Trash emptied successfully.",
                },
            ).data,
            status=200,
        )

    def restore_queryset(self, queryset: QuerySet[_ModelT]) -> None:
        """
        Restore the queryset by updating is_deleted and is_closed fields.
        """
        queryset.update(is_deleted=False)

    @extend_schema(
        request=EmptySerializer,
        responses=ResponseSerializer,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="restore-all",
        url_name="restore_all",
        permission_classes=[AdminGroupOnlyPermission],
    )
    def restore_all(self, request, *args, **kwargs):
        if not self.allow_view_deleted:
            raise Forbidden(
                "Restoring all deleted objects is not allowed for this model.",
                "Restore All Not Allowed",
            )

        queryset = self.model.objects.all_objects().filter(is_deleted=True)

        if not queryset.exists():
            raise BadRequest(
                "No deleted objects to restore.",
                "No Deleted Objects",
            )

        logger.info(
            "Restoring all deleted objects for model: %s by user: %s",
            self.model.__name__,
            request.user.email,
        )
        cache.set(
            f"skip_log_report_activity:{request.user.id}",
            True,
            timeout=60,
        )  # 60 seconds timeout

        try:
            self.restore_queryset(queryset)
            logger.info(
                "Restored all deleted objects for model: %s by user: %s",
                self.model.__name__,
                request.user.email,
            )
        finally:
            cache.delete(f"skip_log_report_activity{request.user.id}")

        return Response(
            ResponseSerializer(
                {
                    "detail": "All deleted objects restored successfully.",
                },
            ).data,
            status=200,
        )


class BaseModelWithCreateOverWriteMixin(BaseModelViewSetMixin[_ModelT]):
    pass
