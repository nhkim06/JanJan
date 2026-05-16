from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Language(models.TextChoices):
        KOREAN = "ko", "Korean"
        JAPANESE = "ja", "Japanese"
        ENGLISH = "en", "English"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    google_sub = models.CharField(max_length=255, unique=True)
    language = models.CharField(max_length=2, choices=Language.choices)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.language})"
