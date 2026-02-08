from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
{%- if cookiecutter.use_async == 'y' %}
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
{%- endif %}
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.views.generic import TemplateView
{%- if cookiecutter.use_drf == 'y' %}
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
{%- endif %}

{%- if cookiecutter.use_drf == 'y' %}
def home(request):
    return redirect(reverse("api-docs"))
{%- endif %}

urlpatterns = [
    path("", 
{%- if cookiecutter.use_drf == 'y' %}
        home,
{% else %}
        TemplateView.as_view(template_name="pages/home.html"), 
{%- endif %}
         name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% raw %}{% url 'admin:index' %}{% endraw %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("{{ cookiecutter.project_slug }}.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
{%- if cookiecutter.use_async == 'y' %}
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
{%- endif %}
{% if cookiecutter.use_drf == 'y' %}
# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF Simple JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
]
{%- endif %}

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("api-auth/", include("rest_framework.urls")),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
