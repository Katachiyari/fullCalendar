from taiga.urls import *  # noqa

from django.urls import include

try:
    from django.conf.urls import url
except Exception:  # pragma: no cover
    from django.urls import re_path as url

# Expose mozilla-django-oidc endpoints under /api/oidc/
urlpatterns += [
    url(r"^api/oidc/", include("mozilla_django_oidc.urls")),
]
