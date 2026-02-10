from django.urls import path

from . import views
from . import views_auth

urlpatterns = [
    path("emails/", views.get_emails, name="get_emails"),
    path("submit/", views.submit_result, name="submit_result"),
    path("interaction/", views.record_interaction),
    path("scenarios/", views.get_scenarios),
    path("register/", views_auth.register, name="register"),
    path("login/", views_auth.login, name="login"),
]
