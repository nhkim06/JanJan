from rest_framework import serializers

from .models import ChatItem


class ChatCreateSerializer(serializers.Serializer):
    formId = serializers.IntegerField()
    question = serializers.CharField(allow_blank=False, trim_whitespace=True)
    category = serializers.CharField(
        allow_blank=True,
        max_length=64,
        required=False,
        trim_whitespace=True,
    )


class ChatListQuerySerializer(serializers.Serializer):
    formId = serializers.IntegerField(required=False)


class ChatItemReadSerializer(serializers.ModelSerializer):
    chatItemId = serializers.IntegerField(source="id")
    formId = serializers.IntegerField(source="form_id")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = ChatItem
        fields = [
            "chatItemId",
            "formId",
            "question",
            "answer",
            "status",
            "createdAt",
            "updatedAt",
        ]
