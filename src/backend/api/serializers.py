from rest_framework import serializers

from .models import Email, InteractionEvent, UserProgress


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
