from django.urls import path

from . import views

urlpatterns = [
    path("emails/", views.get_emails, name="get_emails"),
    path("submit/", views.submit_result, name="submit_result"),
]
