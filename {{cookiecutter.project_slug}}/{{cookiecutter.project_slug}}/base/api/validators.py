from {{ cookiecutter.project_slug }}.base.models import BaseModel
from typing import Type


class UniqueFieldValidator:
    requires_context = True

    def __init__(self, model: Type[BaseModel], field_name: str):
        self.model = model
        self.field_name = field_name

    def __call__(self, value, serializer_field):
        self.model.validate_field_as_unique(
            self.field_name,
            value,
            serializer_field.context.get("pk"),
        )


class UniqueFieldIncludingDeletedValidator:
    requires_context = True

    def __init__(self, model: Type[BaseModel], field_name: str):
        self.model = model
        self.field_name = field_name

    def __call__(self, value, serializer_field):
        self.model.validate_field_as_unique_including_deleted(
            self.field_name,
            value,
            serializer_field.context.get("pk"),
        )
