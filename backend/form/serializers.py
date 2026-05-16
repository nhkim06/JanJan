from rest_framework import serializers

from .models import Form


class FormCreateSerializer(serializers.Serializer):
    category = serializers.CharField(
        allow_blank=True,
        max_length=64,
        required=False,
        trim_whitespace=True,
    )
    answers = serializers.JSONField()
    targetName = serializers.CharField(max_length=255)
    cultureBase = serializers.CharField(max_length=255)

    def validate_answers(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("answers must be an array.")

        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"answers[{index}] must be an object."
                )

            question = item.get("question")
            answer = item.get("answer")
            if not isinstance(question, str) or not (
                isinstance(answer, str) or answer is None
            ):
                raise serializers.ValidationError(
                    f"answers[{index}] must include string question and string/null answer."
                )

        return value

    def create(self, validated_data):
        return Form.objects.create(
            user=self.context["user"],
            category=validated_data.get("category", ""),
            answers=validated_data["answers"],
            target_name=validated_data["targetName"],
            culture_base=validated_data["cultureBase"],
        )


class FormReadSerializer(serializers.ModelSerializer):
    formId = serializers.IntegerField(source="id")
    category = serializers.CharField(source="category")
    targetName = serializers.CharField(source="target_name")
    cultureBase = serializers.CharField(source="culture_base")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = Form
        fields = [
            "formId",
            "category",
            "answers",
            "targetName",
            "cultureBase",
            "createdAt",
            "updatedAt",
        ]
