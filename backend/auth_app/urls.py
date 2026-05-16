from django.urls import path

from .views import CallbackView, LoginView, LogoutView, ProfileView, RegisterView


urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("callback", CallbackView.as_view(), name="callback"),
    path("register", RegisterView.as_view(), name="register"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("profile", ProfileView.as_view(), name="profile"),
]
