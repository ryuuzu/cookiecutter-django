from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from {{ cookiecutter.project_slug }}.users.utils import get_user_prefetch_data


class ReadOnlyPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS and super().has_permission(request, view)


class AdminGroupOnlyPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        user_data = get_user_prefetch_data(request.user)

        has_admin_role = False

        for group in user_data.groups.all():
            if group.name.lower() == "admin":
                has_admin_role = True
                break

        return user_data.is_superuser or has_admin_role


class SuperUserOnlyPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_superuser
