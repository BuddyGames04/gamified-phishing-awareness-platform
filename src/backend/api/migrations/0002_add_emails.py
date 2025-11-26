from django.db import migrations

def seed_emails(apps, schema_editor):
    Email = apps.get_model("api", "Email")

    
    Email.objects.create(
        sender="security1@lloydsbank-notify.com",
        subject="Urgent: Unusual Login attempt Detected on You're Account",
        body=(
            "Dear Customer,\n"
            "We’ve detected a login attempt to your online banking account from a new device in Cambridge, UK. "
            "If this was you, no further action was needed.\n"
            "If this wasn’t you, please secure your account immediately.\n\n"
            "Failure to verify within 24 hours will result in restricted access for your protection\n"
            "Thank you for choosing Lloyds Bank."
        ),
        is_phish=True,
        difficulty=2,
        category="banking"
    )
    Email.objects.create(
        sender="ceo@yourcompany.com",
        subject="Quarterly Results & Strategy Moving Forward",
        body=(
            "Dear Team,\n\n"
            "We’ve closed out another successful quarter with strong performance across all departments. "
            "A full breakdown of our results and upcoming goals will be shared in Monday’s all-hands meeting.\n\n"
            "Thank you for your continued hard work.\n\n"
            "Best,\n"
            "The CEO"
        ),
        is_phish=False,
        difficulty=1,
        category="internal"
    )
    Email.objects.create(
        sender="hr-department@yourcompany-payroll.com",
        subject="Payslip Error - Immediate Attention Required Now",
        body=(
            "Hello,\n"
            "There was an error generating your payslip for this month and your salary may have been misrouted. "
            "We are currently invstigating the issue.\n"
            "To prevent further errors and  verify your details, please fill in this secure form with your banking information.\n\n"
            "Failure to update may delay your payment processing.\n"
            "Regards,\nHuman Resources"
        ),
        is_phish=True,
        difficulty=3,
        category="workplace"
    )
    Email.objects.create(
        sender="studentservices@university.edu",
        subject="Upcoming Semester Registration Deadline",
        body=(
            "Hello,\n\n"
            "This is a reminder that the registration deadline for the upcoming semester is Friday, December 15th. "
            "Ensure your course selections are submitted via the student portal before this date.\n\n"
            "Kind regards,\n"
            "Student Services"
        ),
        is_phish=False,
        difficulty=1,
        category="education"
    )
    Email.objects.create(
        sender="billing@britishgas.co.uk",
        subject="Your Gas and Electricity Bill is Ready",
        body=(
            "Hi,\n\n"
            "Your latest British Gas bill is now available in your online account. "
            "The total for this month is £72.46 and is due by November 30th.\n\n"
            "To view your bill or update your payment method, please log in to your British Gas account.\n\n"
            "Thanks,\n"
            "British Gas"
        ),
        is_phish=False,
        difficulty=2,
        category="billing"
    )
    Email.objects.create(
        sender="notifications@dpd-tracking.uk",
        subject="Your Parcel Couldn’t Be Delivered",
        body=(
            "Hi,\n"
            "Your parcel could not be delivered today because there was no one available to sign for it.\n"
            "Please reschedule your delivery and pay the re-delivery fee (£1.99) via the secure portal.\n\n"
            "Note: If not completed within 48 hours, the parcel will be returned to the sender.\n"
            "DPD Delivery Services"
        ),
        is_phish=True,
        difficulty=2,
        category="logistics"
    )
    Email.objects.create(
        sender="meetings@zoom.us",
        subject="Zoom Meeting Invitation: Team Sync @ 10 AM Thursday",
        body=(
            "You are invited to a scheduled Zoom meeting.\n\n"
            "Topic: Weekly Team Sync\n"
            "Time: Nov 27, 2025 10:00 AM London\n\n"
            "Please join the meeting using your work account via the Zoom app or calendar link.\n\n"
            "— Zoom Scheduler"
        ),
        is_phish=False,
        difficulty=1,
        category="calendar"
    )
    Email.objects.create(
        sender="relief@studentaid-update.com",
        subject="You're Eligible for Immediate Student Loan Forgiveness",
        body=(
            "Congratulations! You’ve been identified as eligible for immediate partial or full forgiveness of your student loans "
            "under the new federal relief plan.\n"
            "To confirm your eligibility, submit your details using the secure portal.\n\n"
            "Act fast — slots are limited and processed on a first-come basis.\n"
            "Student Aid Support Team"
        ),
        is_phish=True,
        difficulty=3,
        category="education"
    )
    Email.objects.create(
        sender="receipts@amazon.co.uk",
        subject="Your Amazon.co.uk Order #203-8459673-5832946",
        body=(
            "Hello,\n\n"
            "Thank you for your purchase. Here are your order details:\n\n"
            "Item: Logitech MX Master 3S Mouse\n"
            "Total: £89.99\n"
            "Estimated Delivery: Nov 28 - Nov 30\n\n"
            "You can track your order from your Amazon account.\n\n"
            "Thanks for shopping with us!\n"
            "— Amazon.co.uk"
        ),
        is_phish=False,
        difficulty=2,
        category="purchase"
    )
    Email.objects.create(
        sender="noreply@github-security.io",
        subject="GitHub Security Alert for Your Repository",
        body=(
            "GitHub has detected a suspicious token push in one of your repositories.\n"
            "To protect your account and prevent unauthorized access, please re-authenticate and review the activity.\n\n"
            "If this action is not taken within 6 hours, we may lock access to affected repositories.\n"
            "GitHub Trust & Safety"
        ),
        is_phish=True,
        difficulty=4,
        category="developer"
    )

    

class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_emails),
    ]
