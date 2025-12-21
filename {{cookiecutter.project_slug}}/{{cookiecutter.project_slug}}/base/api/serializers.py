from typing import Generic, TypeVar

from rest_framework import serializers

from {{ cookiecutter.project_slug }}.base.api.request import BaseRequest
from {{ cookiecutter.project_slug }}.base.models import BaseModel
from {{ cookiecutter.project_slug }}.users.models import User

_ModelT = TypeVar("_ModelT", bound=BaseModel)


class MinimalUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "color")


class EmptySerializer(serializers.Serializer):
    pass


class ResponseSerializer(serializers.Serializer):
    SUCCESS = "success"
    ERROR = "error"

    status_choices = (
        (SUCCESS, SUCCESS),
        (ERROR, ERROR),
    )

    code = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=status_choices, default=SUCCESS)
    title = serializers.CharField(required=False, allow_blank=True)
    detail = serializers.CharField()


class BaseModelSerializer(serializers.ModelSerializer):
    created_by = MinimalUserDetailSerializer(read_only=True)
    updated_by = MinimalUserDetailSerializer(read_only=True)
    deleted_by = MinimalUserDetailSerializer(read_only=True)

    class Meta(Generic[_ModelT]):
        model: _ModelT
        fields = (
            "id",
            "is_deleted",
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
            "locked",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "is_deleted": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "deleted_at": {"read_only": True},
            "locked": {"read_only": True},
        }

    @property
    def request(self) -> BaseRequest | None:
        return self.context.get("request")

    def get_manipulation_data(self, *, all=False) -> dict:
        """
        Returns a dictionary with manipulation data based on the request context.
        This is used to set created_by and updated_by fields.
        """
        manipulation_data = {}
        if self.request:
            if not self.instance or all:
                manipulation_data["created_by"] = self.request.user
            manipulation_data["updated_by"] = self.request.user
        return manipulation_data

    def save(self, **kwargs):
        return super().save(**{**kwargs, **self.get_manipulation_data()})


class RecursiveField(serializers.Field):
    def __init__(self, many=False, **kwargs):
        self.many = many
        super().__init__(**kwargs)

    def to_representation(self, value):
        if value is None:
            return None if not self.many else []

        if self.many:
            # Handle queryset/manager
            if hasattr(value, "all"):
                value = value.all()
            elif hasattr(value, "_prefetched_objects_cache"):
                # Use prefetched data if available
                pass

            return [self._serialize_item(item) for item in value]
        return self._serialize_item(value)

    def _serialize_item(self, item):
        # Create a new serializer instance but it will use prefetched relations
        serializer_class = self.parent.__class__
        serializer = serializer_class(item, context=self.context)
        return serializer.data
