from django.urls import path

from .views import HistoryCreateView, HistoryDetailView, HistoryListView


urlpatterns = [
    path("new", HistoryCreateView.as_view(), name="history-new"),
    path("list", HistoryListView.as_view(), name="history-list"),
    path("<int:history_id>", HistoryDetailView.as_view(), name="history-detail"),
]
