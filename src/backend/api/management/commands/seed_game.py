# src/backend/api/management/commands/seed_game.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import Email, Scenario


def _company_slug(name: str) -> str:
    # simple slug for domains (good enough for seeding)
    s = (
        name.lower()
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("'", "")
    )
    parts = [p for p in s.replace("  ", " ").split(" ") if p]
    return "-".join(parts)


def _mk_domain(company_name: str) -> str:
    return f"{_company_slug(company_name)}.co.uk"


@dataclass(frozen=True)
class ScenarioSeed:
    company_name: str
    sector: str
    role_title: str
    department_name: str
    line_manager_name: str
    responsibilities: List[str]
    intro_text: str


def _scenario_seeds() -> List[ScenarioSeed]:
    return [
        ScenarioSeed(
            company_name="Northbridge Utilities",
            sector="Energy & Utilities",
            role_title="Finance Assistant (Accounts Payable)",
            department_name="Finance",
            line_manager_name="Sandra Patel",
            responsibilities=[
                "Process supplier invoices",
                "Match invoices to purchase orders",
                "Handle supplier queries",
                "Escalate suspected fraud to Finance Manager",
            ],
            intro_text=(
                "You work in Accounts Payable at Northbridge Utilities. "
                "Your role is to process invoices, manage supplier queries, "
                "and support month-end tasks. You regularly receive emails from "
                "suppliers, procurement, and internal finance staff."
            ),
        ),
        ScenarioSeed(
            company_name="Harbourline Logistics",
            sector="Transport & Logistics",
            role_title="Procurement Officer",
            department_name="Procurement",
            line_manager_name="Mark Ellison",
            responsibilities=[
                "Raise purchase orders for approved suppliers",
                "Request quotes and compare bids",
                "Maintain vendor records",
                "Confirm delivery timelines with operations",
            ],
            intro_text=(
                "You work in Procurement at Harbourline Logistics. "
                "Your job is to issue purchase orders and manage vendor communications. "
                "Most emails relate to quotes, deliveries, and supplier onboarding."
            ),
        ),
        ScenarioSeed(
            company_name="Crestview Health Partners",
            sector="Healthcare Services",
            role_title="HR Coordinator",
            department_name="People & Culture",
            line_manager_name="Aisha Khan",
            responsibilities=[
                "Coordinate interviews and onboarding",
                "Process HR paperwork",
                "Support payroll admin requests",
                "Share policy updates internally",
            ],
            intro_text=(
                "You are an HR Coordinator at Crestview Health Partners. "
                "Your inbox includes candidate communications, internal requests, "
                "policy updates, and payroll-related admin."
            ),
        ),
        ScenarioSeed(
            company_name="Stonebrook Council Services",
            sector="Public Sector",
            role_title="Facilities Administrator",
            department_name="Estates & Facilities",
            line_manager_name="Gavin Reid",
            responsibilities=[
                "Manage building access requests",
                "Coordinate maintenance visits",
                "Handle delivery notifications",
                "Update contractors with site requirements",
            ],
            intro_text=(
                "You work in Facilities for Stonebrook Council Services. "
                "You handle building access, contractor scheduling, and maintenance communications."
            ),
        ),
        ScenarioSeed(
            company_name="Bluefin Digital Studio",
            sector="Media & Marketing",
            role_title="Marketing Executive",
            department_name="Marketing",
            line_manager_name="Chloe Simmons",
            responsibilities=[
                "Coordinate campaign assets",
                "Work with external agencies",
                "Manage social scheduling and approvals",
                "Track campaign performance updates",
            ],
            intro_text=(
                "You’re a Marketing Executive at Bluefin Digital Studio. "
                "You receive frequent emails about campaign approvals, shared assets, "
                "agency requests, and platform notifications."
            ),
        ),
        ScenarioSeed(
            company_name="Wellington Retail Group",
            sector="Retail",
            role_title="Customer Support Representative",
            department_name="Customer Operations",
            line_manager_name="Daniel Brooks",
            responsibilities=[
                "Respond to customer tickets",
                "Escalate payment or account issues",
                "Process refunds under policy",
                "Spot suspicious customer messages",
            ],
            intro_text=(
                "You are a Customer Support Rep at Wellington Retail Group. "
                "You handle ticket updates, customer complaints, and account/payment queries."
            ),
        ),
        ScenarioSeed(
            company_name="Kestrel University",
            sector="Higher Education",
            role_title="Research Administrator",
            department_name="Research Office",
            line_manager_name="Dr. Helen Murray",
            responsibilities=[
                "Support grant admin paperwork",
                "Coordinate travel requests",
                "Share research office notices",
                "Manage conference registration invoices",
            ],
            intro_text=(
                "You work in the Research Office at Kestrel University. "
                "You process research admin requests, travel approvals, and grant paperwork."
            ),
        ),
        ScenarioSeed(
            company_name="Redwood Software",
            sector="Technology",
            role_title="IT Service Desk Analyst",
            department_name="IT Support",
            line_manager_name="Priya Desai",
            responsibilities=[
                "Handle password resets and access requests",
                "Triage alerts and service tickets",
                "Assist with device setup",
                "Escalate security incidents",
            ],
            intro_text=(
                "You are an IT Service Desk Analyst at Redwood Software. "
                "You receive access requests, service ticket updates, and security notifications."
            ),
        ),
        ScenarioSeed(
            company_name="Brackenfield Engineering",
            sector="Manufacturing",
            role_title="Project Coordinator",
            department_name="Projects",
            line_manager_name="Tom Gallagher",
            responsibilities=[
                "Schedule project meetings",
                "Chase deliverables and approvals",
                "Manage shared documents",
                "Coordinate external vendor timelines",
            ],
            intro_text=(
                "You’re a Project Coordinator at Brackenfield Engineering. "
                "Your inbox is full of meeting invites, document links, and vendor schedule updates."
            ),
        ),
        ScenarioSeed(
            company_name="Rivergate Financial Advisory",
            sector="Financial Services",
            role_title="Graduate Software Engineer",
            department_name="Engineering",
            line_manager_name="Eleanor Shaw",
            responsibilities=[
                "Work on internal tooling",
                "Respond to CI/build notifications",
                "Handle repo access requests",
                "Follow secure development practices",
            ],
            intro_text=(
                "You’re a Graduate Software Engineer at Rivergate Financial Advisory. "
                "Expect Git/CI alerts, access requests, and internal platform updates."
            ),
        ),
    ]


def _scenario_email_templates(seed: ScenarioSeed) -> List[Dict[str, Any]]:
    """
    Returns ~8 simulation emails per scenario (mix legit + phish).
    Kept template-driven so you can scale easily later.
    """
    domain = _mk_domain(seed.company_name)
    company_slug = _company_slug(seed.company_name)
    mgr = seed.line_manager_name

    # Common “lookalike” domains for phish
    lookalike_1 = f"{company_slug}-secure.com"
    lookalike_2 = f"{company_slug}-verify.com"

    role = seed.role_title.lower()

    # Role-specific flavour
    if "accounts payable" in role or "finance" in role:
        return [
            dict(
                sender_name="Procurement Team",
                sender_email=f"procurement@{domain}",
                subject="PO approval notice: match invoices to PO 48391",
                body=(
                    f"Hi,\n\nFYI PO 48391 has been approved.\n"
                    f"Please match any incoming invoice to this PO.\n\nThanks,\nProcurement"
                ),
                is_phish=False,
                difficulty=1,
                category="procurement",
                links=[],
                attachments=["PO_48391.pdf"],
            ),
            dict(
                sender_name="Accounts Team",
                sender_email=f"accounts@{domain}",
                subject="Month-end close: outstanding supplier invoices",
                body=(
                    f"Hi,\n\nCan you confirm if any invoices are pending approval for month-end?\n"
                    f"Please reply with anything still in your queue.\n\nThanks,\nAccounts"
                ),
                is_phish=False,
                difficulty=2,
                category="finance",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="Supplier Payments",
                sender_email=f"payments@{lookalike_1}",
                subject="Urgent: bank details update required (today)",
                body=(
                    "Hello,\n\nWe’ve updated our bank details.\n"
                    "Please confirm the change today to avoid failed payments.\n\n"
                    "Confirm here:\n"
                    f"http://{lookalike_1}/confirm-payment\n"
                ),
                is_phish=True,
                difficulty=2,
                category="finance",
                links=[f"http://{lookalike_1}/confirm-payment"],
                attachments=[],
            ),
            dict(
                sender_name="Invoice Processing",
                sender_email=f"invoices@{domain}",
                subject="New invoice received: INV-20419",
                body=(
                    "Hi,\n\nA new supplier invoice has been received.\n"
                    "Please review and process within 3 working days.\n\nRegards,\nInvoice Processing"
                ),
                is_phish=False,
                difficulty=1,
                category="finance",
                links=[],
                attachments=["INV-20419.pdf"],
            ),
            dict(
                sender_name=f"{seed.company_name} SharePoint",
                sender_email=f"no-reply@{lookalike_2}",
                subject="Shared file: Supplier_BankChange_Form.pdf",
                body=(
                    "You have been sent a document.\n\n"
                    "Open document to review:\n"
                    f"http://{lookalike_2}/sharepoint/open?id=92831\n"
                ),
                is_phish=True,
                difficulty=3,
                category="it",
                links=[f"http://{lookalike_2}/sharepoint/open?id=92831"],
                attachments=[],
            ),
            dict(
                sender_name=mgr,
                sender_email=f"{mgr.lower().replace(' ', '.')}@{domain}",
                subject="Quick check: supplier query",
                body=(
                    "Hi,\n\nCan you confirm if we paid Westridge Supplies this week?\n"
                    "They’re chasing and I want to reply before 4pm.\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=2,
                category="internal",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="Westridge Supplies",
                sender_email=f"billing@westridgesupplies.co.uk",
                subject="Overdue invoice reminder: INV-20311",
                body=(
                    "Hello,\n\nPlease find attached our overdue invoice INV-20311.\n"
                    "Could you confirm expected payment date?\n\nThank you,\nBilling"
                ),
                is_phish=False,
                difficulty=2,
                category="supplier",
                links=[],
                attachments=["INV-20311.pdf"],
            ),
            dict(
                sender_name="Westridge Supplies",
                sender_email=f"billing@westridge-supplies.co",  # subtle TLD change
                subject="FINAL NOTICE: INV-20311 - immediate action required",
                body=(
                    "Hello,\n\nFINAL NOTICE.\n"
                    "Payment failed. Please re-authorise immediately using the link below:\n"
                    f"http://{company_slug}-paynow.com/retry\n"
                ),
                is_phish=True,
                difficulty=4,
                category="supplier",
                links=[f"http://{company_slug}-paynow.com/retry"],
                attachments=[],
            ),
        ]

    if "it service desk" in role or "service desk" in role:
        return [
            dict(
                sender_name="Service Desk System",
                sender_email=f"no-reply@{domain}",
                subject="New ticket assigned: Password reset request",
                body=(
                    "Ticket #SD-11842 has been assigned to you.\n\n"
                    "Requester: j.smith\nIssue: Password reset\n\n"
                    "Please update the ticket once completed."
                ),
                is_phish=False,
                difficulty=1,
                category="it",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="Microsoft 365",
                sender_email="no-reply@microsoft.com",
                subject="Security alert: Unusual sign-in activity detected",
                body=(
                    "We detected an unusual sign-in attempt.\n"
                    "If this was you, you can ignore this email.\n"
                    "If not, reset your password via your organisation portal."
                ),
                is_phish=False,
                difficulty=2,
                category="security",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="IT Admin Portal",
                sender_email=f"admin@{lookalike_1}",
                subject="Action required: MFA enrollment expiring",
                body=(
                    "Your multi-factor enrollment is expiring.\n"
                    "Re-enroll within 2 hours to avoid lockout:\n"
                    f"http://{lookalike_1}/mfa/re-enroll\n"
                ),
                is_phish=True,
                difficulty=3,
                category="security",
                links=[f"http://{lookalike_1}/mfa/re-enroll"],
                attachments=[],
            ),
            dict(
                sender_name=mgr,
                sender_email=f"{mgr.lower().replace(' ', '.')}@{domain}",
                subject="Laptop setup needed for new starter (Monday)",
                body=(
                    "Hi,\n\nWe’ve got a new starter joining Monday.\n"
                    "Can you prep a laptop and ensure standard apps are installed?\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=1,
                category="internal",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="Printer Support",
                sender_email=f"support@{domain}",
                subject="Printer outage resolved",
                body=(
                    "Hi,\n\nThe printer outage on Floor 2 has been resolved.\n"
                    "No further action required.\n\nRegards,\nIT Support"
                ),
                is_phish=False,
                difficulty=1,
                category="it",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="VPN Team",
                sender_email=f"vpn@{lookalike_2}",
                subject="VPN access upgrade - confirm your account",
                body=(
                    "To complete your VPN access upgrade, confirm your account:\n"
                    f"http://{lookalike_2}/vpn/confirm\n"
                ),
                is_phish=True,
                difficulty=4,
                category="security",
                links=[f"http://{lookalike_2}/vpn/confirm"],
                attachments=[],
            ),
            dict(
                sender_name="Security Operations",
                sender_email=f"soc@{domain}",
                subject="Reminder: report suspicious emails",
                body=(
                    "Reminder: If you receive suspicious emails, do not click links.\n"
                    "Report them using the internal process.\n\nSOC"
                ),
                is_phish=False,
                difficulty=1,
                category="security",
                links=[],
                attachments=[],
            ),
            dict(
                sender_name="Shared Document",
                sender_email=f"no-reply@{lookalike_1}",
                subject="Shared file: AccessReview_Q1.xlsx",
                body=(
                    "A file has been shared with you.\n"
                    "Open:\n"
                    f"http://{lookalike_1}/doc/open?id=40121\n"
                ),
                is_phish=True,
                difficulty=3,
                category="it",
                links=[f"http://{lookalike_1}/doc/open?id=40121"],
                attachments=[],
            ),
        ]

    # Generic pack for other roles (still realistic)
    return [
        dict(
            sender_name=mgr,
            sender_email=f"{mgr.lower().replace(' ', '.')}@{domain}",
            subject="Quick task for today",
            body=(
                "Hi,\n\nCan you take a look at the item we discussed earlier and update me?\n\n"
                f"Thanks,\n{mgr}"
            ),
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="Team Calendar",
            sender_email=f"no-reply@{domain}",
            subject="Meeting invite: Weekly team sync",
            body=(
                "You have been invited to: Weekly team sync\n"
                "When: Thursday 10:00\nWhere: Teams\n"
            ),
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[],
            attachments=["invite.ics"],
        ),
        dict(
            sender_name="Document Sharing",
            sender_email=f"no-reply@{lookalike_1}",
            subject="Shared file: Updated_Policy.pdf",
            body=(
                "A file has been shared with you.\n"
                f"Open here: http://{lookalike_1}/open?id=77219\n"
            ),
            is_phish=True,
            difficulty=3,
            category="it",
            links=[f"http://{lookalike_1}/open?id=77219"],
            attachments=[],
        ),
        dict(
            sender_name="External Partner",
            sender_email="hello@partner-services.co.uk",
            subject="Request for information",
            body=(
                "Hi,\n\nCould you share the latest status update when you have a moment?\n\nThanks,\nPartner"
            ),
            is_phish=False,
            difficulty=2,
            category="external",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="Accounts",
            sender_email=f"accounts@{lookalike_2}",
            subject="Action required: confirm details to avoid interruption",
            body=(
                "We couldn’t verify your details.\n"
                "Confirm now to avoid interruption:\n"
                f"http://{lookalike_2}/confirm\n"
            ),
            is_phish=True,
            difficulty=4,
            category="phish",
            links=[f"http://{lookalike_2}/confirm"],
            attachments=[],
        ),
        dict(
            sender_name="IT Support",
            sender_email=f"support@{domain}",
            subject="Planned maintenance tonight",
            body=(
                "Hi,\n\nPlanned maintenance tonight 22:00–23:00.\n"
                "Some services may be unavailable.\n\nIT Support"
            ),
            is_phish=False,
            difficulty=2,
            category="it",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="Courier",
            sender_email="no-reply@parcel-notify.co",
            subject="Delivery attempted - reschedule",
            body=(
                "We attempted delivery but missed you.\n"
                f"Reschedule: http://{company_slug}-parcel.com/reschedule\n"
            ),
            is_phish=True,
            difficulty=3,
            category="delivery",
            links=[f"http://{company_slug}-parcel.com/reschedule"],
            attachments=[],
        ),
        dict(
            sender_name="Internal Comms",
            sender_email=f"comms@{domain}",
            subject="Reminder: policy training deadline",
            body=(
                "Hi,\n\nReminder: complete the mandatory policy training by Friday.\n\nThanks,\nInternal Comms"
            ),
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[],
            attachments=[],
        ),
    ]


def _arcade_emails() -> List[Dict[str, Any]]:
    # Scenario-free, generic “hot or not” emails
    return [
        dict(
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
        ),
        dict(
            sender_name="Streaming Support",
            sender_email="support@streaming-billing.com",
            subject="Payment failed - update card details",
            body=(
                "Hi,\n\nWe couldn’t process your latest payment.\n"
                "Update your card details to avoid interruption:\n"
                "http://streaming-billing.com/update\n"
            ),
            is_phish=True,
            difficulty=2,
            category="billing",
            links=["http://streaming-billing.com/update"],
            attachments=[],
        ),
        dict(
            sender_name="Delivery Service",
            sender_email="no-reply@parcel-service.co.uk",
            subject="Your parcel is out for delivery",
            body="Hi,\n\nYour parcel is out for delivery today.\n\nThanks,\nDelivery Service",
            is_phish=False,
            difficulty=1,
            category="delivery",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="HMRC",
            sender_email="refunds@hmrc-taxrebate.co",
            subject="Tax refund available",
            body=(
                "Dear Customer,\n\nYou are eligible for a tax refund.\n"
                "Submit details to receive refund:\n"
                "http://hmrc-taxrebate.co/refund\n"
            ),
            is_phish=True,
            difficulty=3,
            category="government",
            links=["http://hmrc-taxrebate.co/refund"],
            attachments=[],
        ),
        dict(
            sender_name="University Admin",
            sender_email="registry@university.ac.uk",
            subject="Timetable update",
            body="Hi,\n\nYour timetable has been updated. Please check the portal.\n\nRegistry",
            is_phish=False,
            difficulty=1,
            category="education",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="Apple ID",
            sender_email="id@appleid-verify.com",
            subject="Apple ID locked - verify now",
            body=(
                "Your Apple ID has been locked due to suspicious activity.\n"
                "Verify now:\n"
                "http://appleid-verify.com/unlock\n"
            ),
            is_phish=True,
            difficulty=3,
            category="account",
            links=["http://appleid-verify.com/unlock"],
            attachments=[],
        ),
        dict(
            sender_name="Gym Membership",
            sender_email="noreply@fitclub.co.uk",
            subject="Welcome to FitClub!",
            body="Hi!\n\nWelcome to FitClub. Your membership is now active.\n\nThanks,\nFitClub",
            is_phish=False,
            difficulty=1,
            category="subscription",
            links=[],
            attachments=[],
        ),
        dict(
            sender_name="Dropbox",
            sender_email="no-reply@dropbox-fileaccess.com",
            subject="Shared folder: Photos",
            body=(
                "A folder has been shared with you.\n"
                "View folder:\n"
                "http://dropbox-fileaccess.com/view\n"
            ),
            is_phish=True,
            difficulty=2,
            category="cloud",
            links=["http://dropbox-fileaccess.com/view"],
            attachments=[],
        ),
    ]


class Command(BaseCommand):
    help = "Seed scenarios and emails for the phishing simulator (simulation + arcade). Safe to run multiple times."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete existing Scenario + simulation emails + arcade emails created by this seed (DANGEROUS).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        wipe = bool(options.get("wipe"))

        if wipe:
            # Wipe ALL scenarios and ALL emails.
            # If we need selective wipe later, add a 'seed_tag' field.
            Email.objects.all().delete()
            Scenario.objects.all().delete()
            self.stdout.write(self.style.WARNING("WIPED: all Email + Scenario rows."))

        created_scenarios = 0
        created_sim_emails = 0
        created_arcade_emails = 0

        # --- Scenarios + simulation emails ---
        for s in _scenario_seeds():
            scenario, s_created = Scenario.objects.update_or_create(
                company_name=s.company_name,
                role_title=s.role_title,
                defaults=dict(
                    sector=s.sector,
                    department_name=s.department_name,
                    line_manager_name=s.line_manager_name,
                    responsibilities=s.responsibilities,
                    intro_text=s.intro_text,
                ),
            )
            if s_created:
                created_scenarios += 1

            for e in _scenario_email_templates(s):
                # Natural key: scenario + sender_email + subject + mode
                email, e_created = Email.objects.update_or_create(
                    scenario=scenario,
                    mode="simulation",
                    sender_email=e["sender_email"],
                    subject=e["subject"],
                    defaults=dict(
                        sender_name=e["sender_name"],
                        body=e["body"],
                        is_phish=e["is_phish"],
                        difficulty=e["difficulty"],
                        category=e.get("category"),
                        links=e.get("links", []) or [],
                        attachments=e.get("attachments", []) or [],
                    ),
                )
                if e_created:
                    created_sim_emails += 1

        # --- Arcade emails ---
        for e in _arcade_emails():
            email, e_created = Email.objects.update_or_create(
                scenario=None,
                mode="arcade",
                sender_email=e["sender_email"],
                subject=e["subject"],
                defaults=dict(
                    sender_name=e["sender_name"],
                    body=e["body"],
                    is_phish=e["is_phish"],
                    difficulty=e["difficulty"],
                    category=e.get("category"),
                    links=e.get("links", []) or [],
                    attachments=e.get("attachments", []) or [],
                ),
            )
            if e_created:
                created_arcade_emails += 1

        # Summary
        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(
            f"- Scenarios: +{created_scenarios} (total {Scenario.objects.count()})"
        )
        self.stdout.write(
            f"- Simulation emails: +{created_sim_emails} (total {Email.objects.filter(mode='simulation').count()})"
        )
        self.stdout.write(
            f"- Arcade emails: +{created_arcade_emails} (total {Email.objects.filter(mode='arcade').count()})"
        )
        self.stdout.write(
            self.style.NOTICE(
                "Run: docker compose exec backend python manage.py seed_game\n"
                "Optional wipe: docker compose exec backend python manage.py seed_game --wipe"
            )
        )
