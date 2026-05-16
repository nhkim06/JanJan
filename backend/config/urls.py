"""
URL configuration for the JanJan backend.
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("auth_app.urls")),
    path("api/", include("api.urls")),
    path("chat/", include("chat.urls")),
    path("form/", include("form.urls")),
    path("history/", include("history.urls")),
]
