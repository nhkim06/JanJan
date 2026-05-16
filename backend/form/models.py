from django.conf import settings
from django.db import models


class Form(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forms",
    )
    category = models.CharField(max_length=64, blank=True, default="")
    answers = models.JSONField()
    target_name = models.CharField(max_length=255)
    culture_base = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form #{self.pk} for {self.target_name}"
