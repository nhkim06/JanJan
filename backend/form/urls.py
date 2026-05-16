from django.urls import path

from .views import FormCreateView, FormDetailView, FormListView


urlpatterns = [
    path("new", FormCreateView.as_view(), name="form-new"),
    path("list", FormListView.as_view(), name="form-list"),
    path("<int:form_id>", FormDetailView.as_view(), name="form-detail"),
]
