from rest_framework import serializers

from .models import History


class HistoryWriteSerializer(serializers.Serializer):
    targetName = serializers.CharField(max_length=255)
    received = serializers.BooleanField()
    value = serializers.IntegerField()
    cultureBase = serializers.CharField(max_length=20)
    category = serializers.CharField(allow_blank=False, trim_whitespace=True)
    date = serializers.DateField()

    def create(self, validated_data):
        return History.objects.create(
            user=self.context["user"],
            target_name=validated_data["targetName"],
            received=validated_data["received"],
            value=validated_data["value"],
            culture_base=validated_data["cultureBase"],
            category=validated_data["category"],
            date=validated_data["date"],
        )

    def update(self, instance, validated_data):
        instance.target_name = validated_data["targetName"]
        instance.received = validated_data["received"]
        instance.value = validated_data["value"]
        instance.culture_base = validated_data["cultureBase"]
        instance.category = validated_data["category"]
        instance.date = validated_data["date"]
        instance.save(
            update_fields=[
                "target_name",
                "received",
                "value",
                "culture_base",
                "category",
                "date",
                "updated_at",
            ]
        )
        return instance


class HistoryReadSerializer(serializers.ModelSerializer):
    historyId = serializers.IntegerField(source="id")
    targetName = serializers.CharField(source="target_name")
    cultureBase = serializers.CharField(source="culture_base")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = History
        fields = [
            "historyId",
            "targetName",
            "received",
            "value",
            "cultureBase",
            "category",
            "date",
            "createdAt",
            "updatedAt",
        ]
