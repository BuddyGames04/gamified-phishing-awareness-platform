from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Email, UserProgress
from .serializers import EmailSerializer, UserProgressSerializer

@api_view(["GET"])
def get_emails(request):
    emails = Email.objects.all()
    serializer = EmailSerializer(emails, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def submit_result(request):
    user_id = request.data.get("user_id")
    is_correct = request.data.get("is_correct")

    progress, _ = UserProgress.objects.get_or_create(user_id=user_id)
    progress.total_attempts += 1
    if is_correct:
        progress.correct += 1
        progress.score += 10
    else:
        progress.incorrect += 1
        progress.score = max(progress.score - 2, 0)
    progress.save()

    serializer = UserProgressSerializer(progress)
    return Response(serializer.data)
