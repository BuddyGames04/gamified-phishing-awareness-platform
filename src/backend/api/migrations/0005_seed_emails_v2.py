from django.db import migrations


def seed_emails(apps, schema_editor):
    Email = apps.get_model("api", "Email")

    Email.objects.all().delete()  # optional: avoid duplicates

    Email.objects.create(
        sender_name="Lloyds Bank Security",
        sender_email="security1@lloydsbank-notify.com",
        subject="Urgent: Unusual Login attempt Detected on Your Account",
        body=(
            "Dear Customer,\n"
            "We’ve detected a login attempt to your online banking account from a new device in Cambridge, UK.\n"
            "If this wasn’t you, please secure your account immediately.\n\n"
            "Failure to verify within 24 hours will result in restricted access.\n"
        ),
        is_phish=True,
        difficulty=2,
        category="banking",
        links=["http://lloydsbank-notify.com/verify"],
        attachments=["SecurityReport.pdf"],
    )

    Email.objects.create(
        sender_name="Company CEO",
        sender_email="ceo@yourcompany.com",
        subject="Quarterly Results & Strategy Moving Forward",
        body=(
            "Dear Team,\n\n"
            "We’ve closed out another strong quarter. Full breakdown Monday.\n\n"
            "Best,\nThe CEO"
        ),
        is_phish=False,
        difficulty=1,
        category="internal",
        links=[],
        attachments=[],
    )

    # Add the rest here
    # and add some links/attachments to the phishy ones)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_remove_email_sender_email_sender_email_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_emails),
    ]
