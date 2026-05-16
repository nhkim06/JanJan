from django.urls import path

from .views import ChatCreateView, ChatListView


urlpatterns = [
    path("new", ChatCreateView.as_view(), name="chat-new"),
    path("list", ChatListView.as_view(), name="chat-list"),
]
