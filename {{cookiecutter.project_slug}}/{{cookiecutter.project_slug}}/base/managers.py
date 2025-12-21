from django.db import models


class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_objects(self):
        return super().get_queryset()

    def deleted(self):
        return super().get_queryset().filter(is_deleted=True)

    def get_object(self, pk):
        return super().get_queryset().get(pk=pk)

    def get_object_or_none(self, pk):
        try:
            return super().get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return None
