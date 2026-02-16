from rest_framework import serializers
from .models import LevelRun, EmailDecisionEvent, Level, Scenario, Email

class StartRunSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    mode = serializers.ChoiceField(choices=["simulation", "arcade"], default="simulation")
    scenario_id = serializers.IntegerField(required=False, allow_null=True)
    level_number = serializers.IntegerField()
    emails_total = serializers.IntegerField(min_value=0)

class StartRunResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelRun
        fields = ["id", "user_id", "mode", "scenario_id", "level_number", "emails_total", "started_at"]

class CompleteRunSerializer(serializers.Serializer):
    correct = serializers.IntegerField(min_value=0)
    incorrect = serializers.IntegerField(min_value=0)

class DecisionCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    run_id = serializers.IntegerField(required=False, allow_null=True)
    email_id = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=["report_phish", "mark_read", "mark_safe"])
    was_correct = serializers.BooleanField()
