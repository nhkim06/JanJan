from django.db import models


class ChatItem(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"

    form = models.ForeignKey(
        "form.Form",
        on_delete=models.CASCADE,
        related_name="chat_items",
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatItem #{self.pk} ({self.status})"
