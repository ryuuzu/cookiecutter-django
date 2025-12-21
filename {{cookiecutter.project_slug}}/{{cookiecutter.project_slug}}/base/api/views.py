from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from {{ cookiecutter.project_slug }}.base.api.mixins import (
    BaseModelViewSetMixin,
    BaseModelWithCreateOverWriteMixin,
)


class BaseModelViewSet(BaseModelWithCreateOverWriteMixin, ModelViewSet):
    pass


class BaseModelReadOnlyViewSet(BaseModelViewSetMixin, ReadOnlyModelViewSet):
    pass
