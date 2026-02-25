from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from api.management.seeders.common import clamp_difficulty, company_slug, mk_domain
from api.models import Email, Scenario


@dataclass(frozen=True)
class ScenarioSeed:
    company_name: str
    sector: str
    role_title: str
    department_name: str
    line_manager_name: str
    responsibilities: list[str]
    intro_text: str


def scenario_seeds() -> list[ScenarioSeed]:
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


def scenario_email_templates(seed: ScenarioSeed) -> list[dict[str, Any]]:
    dom = mk_domain(seed.company_name)
    company = company_slug(seed.company_name)
    mgr_clean = (
        seed.line_manager_name.replace(".", "")
        .replace(",", "")
        .lower()
        .replace(" ", ".")
    )
    mgr = seed.line_manager_name
    lookalike_1 = f"{company}-secure.com"
    lookalike_2 = f"{company}-verify.com"
    role = seed.role_title.lower()

    if "accounts payable" in role or "finance" in role:
        return [
            dict(
                sender_name="Procurement Team",
                sender_email=f"procurement@{dom}",
                subject="PO approval notice: match invoices to PO 48391",
                body=(
                    "Hi,\n\nFYI PO 48391 has been approved.\n"
                    "Please match any incoming invoice to this PO.\n\nThanks,\nProcurement"
                ),
                is_phish=False,
                difficulty=1,
                category="procurement",
                links=[],
                attachments=["PO_48391.pdf"],
            ),
            dict(
                sender_name="Accounts Team",
                sender_email=f"accounts@{dom}",
                subject="Month-end close: outstanding supplier invoices",
                body=(
                    "Hi,\n\nCan you confirm if any invoices are pending approval for month-end?\n"
                    "Please reply with anything still in your queue.\n\nThanks,\nAccounts"
                ),
                is_phish=False,
                difficulty=2,
                category="finance",
                links=[f"https://{dom}/finance/month-end/outstanding"],
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
                sender_email=f"invoices@{dom}",
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
                sender_email=f"{mgr_clean}@{dom}",
                subject="Quick check: supplier query",
                body=(
                    "Hi,\n\nCan you confirm if we paid Westridge Supplies this week?\n"
                    "They’re chasing and I want to reply before 4pm.\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=2,
                category="internal",
                links=[f"https://{dom}/finance/payments/status"],
                attachments=[],
            ),
            dict(
                sender_name="Westridge Supplies",
                sender_email="billing@westridgesupplies.co.uk",
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
                sender_email="billing@westridge-supplies.co",
                subject="FINAL NOTICE: INV-20311 - immediate action required",
                body=(
                    "Hello,\n\nFINAL NOTICE.\n"
                    "Payment failed. Please re-authorise immediately using the link below:\n"
                    f"http://{company}-paynow.com/retry\n"
                ),
                is_phish=True,
                difficulty=4,
                category="supplier",
                links=[f"http://{company}-paynow.com/retry"],
                attachments=[],
            ),
        ]

    if "it service desk" in role or "service desk" in role:
        return [
            dict(
                sender_name="Service Desk System",
                sender_email=f"no-reply@{dom}",
                subject="New ticket assigned: Password reset request",
                body=(
                    "Ticket #SD-11842 has been assigned to you.\n\n"
                    "Requester: j.smith\nIssue: Password reset\n\n"
                    "Please update the ticket once completed."
                ),
                is_phish=False,
                difficulty=1,
                category="it",
                links=[f"https://{dom}/servicedesk/tickets/SD-11842"],
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
                links=[f"https://{dom}/security/alerts"],
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
                sender_email=f"{mgr_clean}@{dom}",
                subject="Laptop setup needed for new starter (Monday)",
                body=(
                    "Hi,\n\nWe’ve got a new starter joining Monday.\n"
                    "Can you prep a laptop and ensure standard apps are installed?\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=1,
                category="internal",
                links=[f"https://{dom}/it/requests/new-starter"],
                attachments=[],
            ),
            dict(
                sender_name="Printer Support",
                sender_email=f"support@{dom}",
                subject="Printer outage resolved",
                body=(
                    "Hi,\n\nThe printer outage on Floor 2 has been resolved.\n"
                    "No further action required.\n\nRegards,\nIT Support"
                ),
                is_phish=False,
                difficulty=1,
                category="it",
                links=[f"https://{dom}/it/status"],
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
                sender_email=f"soc@{dom}",
                subject="Reminder: report suspicious emails",
                body=(
                    "Reminder: If you receive suspicious emails, do not click links.\n"
                    "Report them using the internal process.\n\nSOC"
                ),
                is_phish=False,
                difficulty=1,
                category="security",
                links=[f"https://{dom}/security/report-phishing"],
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

    return [
        dict(
            sender_name=mgr,
            sender_email=f"{mgr_clean}@{dom}",
            subject="Quick task for today",
            body=(
                "Hi,\n\nCan you take a look at the item we discussed earlier and update me?\n\n"
                f"Thanks,\n{mgr}"
            ),
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[f"https://{dom}/tasks/today"],
            attachments=[],
        ),
        dict(
            sender_name="Team Calendar",
            sender_email=f"no-reply@{dom}",
            subject="Meeting invite: Weekly team sync",
            body="You have been invited to: Weekly team sync\nWhen: Thursday 10:00\nWhere: Teams\n",
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
            body=f"A file has been shared with you.\nOpen here: http://{lookalike_1}/open?id=77219\n",
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
            body="Hi,\n\nCould you share the latest status update when you have a moment?\n\nThanks,\nPartner",
            is_phish=False,
            difficulty=2,
            category="external",
            links=["https://partner-services.co.uk/portal/requests"],
            attachments=[],
        ),
        dict(
            sender_name="Accounts",
            sender_email=f"accounts@{lookalike_2}",
            subject="Action required: confirm details to avoid interruption",
            body=f"We couldn’t verify your details.\nConfirm now to avoid interruption:\nhttp://{lookalike_2}/confirm\n",
            is_phish=True,
            difficulty=4,
            category="phish",
            links=[f"http://{lookalike_2}/confirm"],
            attachments=[],
        ),
        dict(
            sender_name="IT Support",
            sender_email=f"support@{dom}",
            subject="Planned maintenance tonight",
            body="Hi,\n\nPlanned maintenance tonight 22:00–23:00.\nSome services may be unavailable.\n\nIT Support",
            is_phish=False,
            difficulty=2,
            category="it",
            links=[f"https://{dom}/it/maintenance"],
            attachments=[],
        ),
        dict(
            sender_name="Courier",
            sender_email="no-reply@parcel-notify.co",
            subject="Delivery attempted - reschedule",
            body=f"We attempted delivery but missed you.\nReschedule: http://{company}-parcel.com/reschedule\n",
            is_phish=True,
            difficulty=3,
            category="delivery",
            links=[f"http://{company}-parcel.com/reschedule"],
            attachments=[],
        ),
        dict(
            sender_name="Internal Comms",
            sender_email=f"comms@{dom}",
            subject="Reminder: policy training deadline",
            body="Hi,\n\nReminder: complete the mandatory policy training by Friday.\n\nThanks,\nInternal Comms",
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[f"https://{dom}/training/mandatory"],
            attachments=[],
        ),
    ]


def seed_scenarios_and_simulation_emails(*, stdout=None, style=None) -> tuple[int, int]:
    created_scenarios = 0
    created_sim_emails = 0

    for seed in scenario_seeds():
        scenario, s_created = Scenario.objects.update_or_create(
            company_name=seed.company_name,
            role_title=seed.role_title,
            defaults=dict(
                sector=seed.sector,
                department_name=seed.department_name,
                line_manager_name=seed.line_manager_name,
                responsibilities=seed.responsibilities,
                intro_text=seed.intro_text,
            ),
        )
        if s_created:
            created_scenarios += 1

        for e in scenario_email_templates(seed):
            email, e_created = Email.objects.update_or_create(
                scenario=scenario,
                mode="simulation",
                sender_email=e["sender_email"],
                subject=e["subject"],
                defaults=dict(
                    sender_name=e["sender_name"],
                    body=e["body"],
                    is_phish=e["is_phish"],
                    difficulty=clamp_difficulty(e.get("difficulty", 1)),
                    category=e.get("category"),
                    links=e.get("links", []) or [],
                    attachments=e.get("attachments", []) or [],
                ),
            )
            email.full_clean()
            email.save()
            if e_created:
                created_sim_emails += 1

    if stdout and style:
        stdout.write(style.SUCCESS("Seeded scenarios + simulation template emails."))

    return created_scenarios, created_sim_emails
