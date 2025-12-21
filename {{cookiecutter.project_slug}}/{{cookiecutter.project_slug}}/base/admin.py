from django.contrib import admin

from {{ cookiecutter.project_slug }}.base.models import BaseModel


class BaseModelAdmin(admin.ModelAdmin):
    model: BaseModel
    list_display = ["is_deleted"]
    list_filter = ["is_deleted"]
    actions = ["restore"]

    def restore(self, request, queryset):
        queryset.filter(is_deleted=True).update(
            is_deleted=False, deleted_at=None, deleted_by=None
        )

    restore.short_description = "Restore selected %(verbose_name_plural)s"

    def get_queryset(self, request):
        return self.model.objects.all_objects()
