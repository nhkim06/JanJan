from django.conf import settings
from django.db import models
from django.utils import timezone


class History(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="histories",
    )
    target_name = models.CharField(max_length=255)
    received = models.BooleanField(default=True)
    value = models.IntegerField()
    currency = models.CharField(max_length=20, default="ko")
    category = models.TextField()
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"History #{self.pk} for {self.target_name}"
