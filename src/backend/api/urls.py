from django.urls import path

from . import views, views_auth, views_arcade
from .views_metrics import (
    CompleteLevelRunView,
    CreateDecisionEventView,
    ProfileMetricsView,
    StartLevelRunView,
)

urlpatterns = [
    path("emails/", views.get_emails, name="get_emails"),
    path("submit/", views.submit_result, name="submit_result"),
    path("interaction/", views.record_interaction),
    path("scenarios/", views.get_scenarios),
    path("register/", views_auth.register, name="register"),
    path("login/", views_auth.login, name="login"),
    path("metrics/level-runs/start/", StartLevelRunView.as_view()),
    path("metrics/level-runs/<int:run_id>/complete/", CompleteLevelRunView.as_view()),
    path("metrics/decisions/", CreateDecisionEventView.as_view()),
    path("profile/metrics/", ProfileMetricsView.as_view()),
    path("arcade/next/", views_arcade.get_arcade_next, name="arcade_next"),
    path("arcade/attempt/", views_arcade.post_arcade_attempt, name="arcade_attempt"),
]
