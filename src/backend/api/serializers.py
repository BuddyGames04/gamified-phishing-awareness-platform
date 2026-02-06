from rest_framework import serializers
from .models import Email, InteractionEvent, UserProgress, Scenario


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = "__all__"


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
