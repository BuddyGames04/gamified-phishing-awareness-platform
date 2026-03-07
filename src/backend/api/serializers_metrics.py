from rest_framework import serializers

from .models import Email, EmailDecisionEvent, Level, LevelRun, Scenario


class StartRunSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    mode = serializers.ChoiceField(
        choices=["simulation", "arcade", "pvp"], default="simulation"
    )
    scenario_id = serializers.IntegerField(required=False, allow_null=True)
    level_number = serializers.IntegerField()
    emails_total = serializers.IntegerField(min_value=0)
    pvp_level_id = serializers.IntegerField(required=False, allow_null=True)


class StartRunResponseSerializer(serializers.ModelSerializer):
    pvp_level_id = serializers.SerializerMethodField()

    class Meta:
        model = LevelRun
        fields = [
            "id",
            "user_id",
            "mode",
            "scenario_id",
            "level_number",
            "emails_total",
            "started_at",
            "pvp_level_id",
        ]

    def get_pvp_level_id(self, obj):
        return getattr(obj, "pvp_level_id", None)


class CompleteRunSerializer(serializers.Serializer):
    correct = serializers.IntegerField(min_value=0)
    incorrect = serializers.IntegerField(min_value=0)
    duration_ms = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    points = serializers.IntegerField(required=False, allow_null=True)
    client_duration_ms = serializers.IntegerField(required=False, allow_null=True)


class DecisionCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    run_id = serializers.IntegerField(required=False, allow_null=True)
    email_id = serializers.IntegerField()
    decision = serializers.ChoiceField(
        choices=["report_phish", "mark_read", "mark_safe"]
    )
    was_correct = serializers.BooleanField()