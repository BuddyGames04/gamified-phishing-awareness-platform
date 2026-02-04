from django.db import migrations


def seed_emails(apps, schema_editor):
    Email = apps.get_model("api", "Email")

    Email.objects.create(
    sender_name="Lloyds Bank Security",
    sender_email="security1@lloydsbank-notify.com",
    subject="Urgent: Unusual Login attempt Detected on You're Account",
    body=(...),
    is_phish=True,
    difficulty=2,
    category="banking",
    links=["http://lloydsbank-notify.com/verify"],
    attachments=[],
)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [

    ]
