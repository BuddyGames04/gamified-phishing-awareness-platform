from rest_framework import serializers

from .models import Email, InteractionEvent, Scenario, UserProgress


class EmailSerializer(serializers.ModelSerializer):
    current_level_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Email
        fields = [
                "id",
                "sender_name",
                "sender_email",
                "subject",
                "body",
                "is_phish",
                "difficulty",
                "category",
                "created_at",
                "links",
                "attachments",
                "mode",
                "scenario",
                "current_level_number",
            ]


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = "__all__"


class InteractionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionEvent
        fields = "__all__"


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
