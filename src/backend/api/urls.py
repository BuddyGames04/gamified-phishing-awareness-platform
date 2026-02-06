from django.urls import path

from . import views
from .views import record_interaction


urlpatterns = [
    path("emails/", views.get_emails, name="get_emails"),
    path("submit/", views.submit_result, name="submit_result"),
    path("interaction/", record_interaction),
]
