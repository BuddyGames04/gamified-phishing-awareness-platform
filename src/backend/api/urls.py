from django.urls import path

from . import views, views_arcade, views_auth, views_pvp
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
    # --------------------
    # PVP
    # --------------------
    path("pvp/scenarios/mine/", views_pvp.pvp_scenarios_mine),
    path("pvp/scenarios/", views_pvp.pvp_scenarios_create),
    path("pvp/scenarios/<int:scenario_id>/", views_pvp.pvp_scenarios_detail),
    path("pvp/levels/mine/", views_pvp.pvp_levels_mine),
    path("pvp/levels/posted/", views_pvp.pvp_levels_posted),
    path("pvp/levels/", views_pvp.pvp_levels_create),
    path("pvp/levels/<int:level_id>/", views_pvp.pvp_levels_detail),
    path("pvp/levels/<int:level_id>/publish/", views_pvp.pvp_levels_publish),
    path("pvp/levels/<int:level_id>/emails/", views_pvp.pvp_level_emails_list),
    path("pvp/levels/<int:level_id>/emails/create/", views_pvp.pvp_level_emails_create),
    path(
        "pvp/levels/<int:level_id>/emails/<int:email_id>/",
        views_pvp.pvp_level_emails_detail,
    ),
    path("pvp/play/emails/", views_pvp.pvp_play_emails),
]
