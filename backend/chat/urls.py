from django.urls import path

from .views import ChatCreateView, ChatDetailView, ChatListView


urlpatterns = [
    path("new", ChatCreateView.as_view(), name="chat-new"),
    path("list", ChatListView.as_view(), name="chat-list"),
    path("<int:chat_item_id>", ChatDetailView.as_view(), name="chat-detail"),
]
