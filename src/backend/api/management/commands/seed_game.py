# src/backend/api/management/commands/seed_game.py

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import Email, Level, LevelEmail, Scenario


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
    # Clean up manager name for use in email addresses (remove special chars)
    mgr_clean = (
        seed.line_manager_name.replace(".", "")
        .replace(",", "")
        .lower()
        .replace(" ", ".")
    )
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
                links=[f"https://{domain}/finance/month-end/outstanding"],
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
                sender_email=f"{mgr_clean}@{domain}",
                subject="Quick check: supplier query",
                body=(
                    "Hi,\n\nCan you confirm if we paid Westridge Supplies this week?\n"
                    "They’re chasing and I want to reply before 4pm.\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=2,
                category="internal",
                links=[f"https://{domain}/finance/payments/status"],
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
                links=[f"https://{domain}/servicedesk/tickets/SD-11842"],
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
                links=[f"https://{domain}/security/alerts"],
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
                sender_email=f"{mgr_clean}@{domain}",
                subject="Laptop setup needed for new starter (Monday)",
                body=(
                    "Hi,\n\nWe’ve got a new starter joining Monday.\n"
                    "Can you prep a laptop and ensure standard apps are installed?\n\nThanks,\n"
                    f"{mgr}"
                ),
                is_phish=False,
                difficulty=1,
                category="internal",
                links=[f"https://{domain}/it/requests/new-starter"],
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
                links=[f"https://{domain}/it/status"],
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
                links=[f"https://{domain}/security/report-phishing"],
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
            sender_email=f"{mgr_clean}@{domain}",
            subject="Quick task for today",
            body=(
                "Hi,\n\nCan you take a look at the item we discussed earlier and update me?\n\n"
                f"Thanks,\n{mgr}"
            ),
            is_phish=False,
            difficulty=1,
            category="internal",
            links=[f"https://{domain}/tasks/today"],
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
            links=["https://partner-services.co.uk/portal/requests"],
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
            links=[f"https://{domain}/it/maintenance"],
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
            links=[f"https://{domain}/training/mandatory"],
            attachments=[],
        ),
    ]
def _clean_name_to_email_localpart(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace("'", "")
        .replace(".", "")
        .replace(",", "")
        .replace("  ", " ")
        .strip()
        .replace(" ", ".")
    )

def _pick_one(a: list[str]) -> str:
    return random.choice(a)

def _make_attachment(filename: str) -> list[str]:
    return [filename]

def _make_link(url: str) -> list[str]:
    return [url]

def _ensure_xor_links_attachments(e: dict) -> dict:
    links = e.get("links") or []
    atts = e.get("attachments") or []
    if (len(links) > 0) == (len(atts) > 0):
        raise ValueError(
            f"Arcade email violates XOR invariant: subject={e.get('subject')} links={links} attachments={atts}"
        )
    return e

def _maybe(prob: float) -> bool:
    return random.random() < prob

def _clamp_difficulty(d: int) -> int:
    # Model + UI expect 1..5
    return max(1, min(5, int(d)))

def _bad_url_variants(url: str) -> str:
    # Deliberately awful "pisstake" URL mutations (diff 1)
    variants = [
        url.replace("https://", "http//"),          # missing colon
        url.replace("https://", "hxxp://"),         # hxxp
        url.replace("https://", "http://").replace(".", " ."),  # space breaks
        url.replace("https://", ""),                # naked domain/path
        url.replace("https://", "http://").replace(".co.uk", ".con"),  # .con
        url.replace("https://", "http://").replace("/", " / "),        # spaced
    ]
    return random.choice(variants)


def _userinfo_trick(real_domain: str, evil_domain: str, path: str) -> str:
    # Very realistic "looks legit at a glance" trick.
    # Browser goes to evil_domain; many humans only see real_domain before '@'.
    return f"https://{real_domain}@{evil_domain}/{path.lstrip('/')}"


def _lookalike_domain(domain: str, difficulty: int) -> str:
    """
    Make a lookalike domain with increasing subtlety.

    difficulty 2: obvious
    difficulty 3: moderate
    difficulty 4: subtle
    difficulty 5: very subtle
    """
    base = domain.replace(".co.uk", "").replace(".com", "").replace(".ac.uk", "")
    tld = ".co.uk" if domain.endswith(".co.uk") else ".com"

    if difficulty <= 2:
        return f"{base}-verify{tld}"
    if difficulty == 3:
        return f"{base}-security{tld}"
    if difficulty == 4:
        # Subdomain-like bait
        return f"secure.{base}{tld}.login"
    # difficulty 5: close + boring
    return f"{base}-portal{tld}"


def _attachment_for(diff: int, kind: str, is_phish: bool) -> str:
    """
    Attachment names signal varies with difficulty.
    Diff 5 phish can look benign.
    """
    safe_pdfs = [
        "Invoice.pdf",
        "Statement.pdf",
        "RemittanceAdvice.pdf",
        "Updated_Policy.pdf",
        "P45_Request.pdf",
        "Payroll_Update.pdf",
    ]
    safe_office = [
        "Meeting_Notes.docx",
        "Onboarding_Checklist.docx",
        "Budget_Summary.xlsx",
        "Timesheet.xlsx",
    ]
    risky = [
        "Invoice.pdf.exe",
        "Invoice.pdf.scr",
        "RemittanceAdvice.pdf.iso",
        "Document_View.htm",
        "PaymentAdvice.docm",
        "Quote.xlsm",
    ]

    if not is_phish:
        # legit: mostly safe
        return random.choice(safe_pdfs + safe_office)

    # phish:
    if diff == 1:
        return random.choice(["FREE_GIFT_CARD.exe", "invoiceeeee.pdf.exe", "voicemail.htm", "open_me_now.scr"])
    if diff == 2:
        return random.choice(risky)
    if diff == 3:
        return random.choice(risky + ["Invoice_2026-02.pdf.iso", "PaymentAdvice.docm"])
    if diff == 4:
        return random.choice(["Invoice.pdf.iso", "RemittanceAdvice.docm", "Statement.pdf.exe"])
    # diff 5: “near indistinguishable”
    # still phish in labels, but attachment name is clean
    return random.choice(safe_pdfs)


def _arcade_emails() -> List[Dict[str, Any]]:
    """
    Scenario-free arcade emails with genuine difficulty progression.
    - Diff 1: pisstake (broken links/typos)
    - Diff 2: obvious (brand/domain mismatch, shouty urgency)
    - Diff 3: average (plausible copy, modest lookalikes)
    - Diff 4: head-scratching (subdomain tricks, plausible portals, reduced urgency)
    - Diff 5: spear-ish (userinfo trick, benign-looking attachments, polished copy)
    XOR invariant enforced (exactly one of links/attachments is non-empty).
    """
    emails: List[Dict[str, Any]] = []

    # Brands (fake-real for simulator)
    BANKS = ["NatWest", "Barclays", "Lloyds", "HSBC", "Santander"]
    DELIVERY = ["Royal Mail", "DPD", "Evri", "DHL", "UPS"]
    CLOUD = ["Dropbox", "OneDrive", "Google Drive", "WeTransfer", "DocuSign"]
    MARKET = ["Amazon", "eBay", "PayPal", "Vinted"]
    ORGS = ["FitClub", "CityGym", "SwimCentre", "CinemaPass", "LibraryPlus"]
    UNIS = ["Kestrel University", "Northbridge University", "Southwick University"]

    # “Legit” base domains for the simulator
    LEGIT_PORTAL = {
        "bank": "secure-notifications.co.uk",
        "delivery": "parcel-service.co.uk",
        "cloud": "portal-services.co.uk",
        "membership": "memberships.co.uk",
        "uni": "university.ac.uk",
        "market": "account-portal.co.uk",
    }

    def _url_in_body(diff: int) -> bool:
        diff = _clamp_difficulty(diff)

        # Body URLs are an easy tell. Keep them mostly to low diffs.
        if diff <= 2:
            return True

        # diff 3+: mostly no raw URL in body
        # diff 5: almost never include raw URL (spear tends to hide behind a button)
        if diff == 5:
            return _maybe(0.03)
        if diff == 4:
            return _maybe(0.08)
        return _maybe(0.15)

    def _format_body_with_optional_url(diff: int, body: str, url: Optional[str]) -> str:
        if not url:
            return body
        if not _url_in_body(diff):
            # Don't paste raw URL; pretend “button”
            return body + "\n\nOpen the link using the button above in the email client.\n"
        return body + f"\n\nLink:\n{url}\n"

    def _make_legit_email(diff: int) -> Dict[str, Any]:
        diff = _clamp_difficulty(diff)
        kind = random.choice(["delivery", "cloud", "membership", "uni", "invoice"])
        ref = random.randint(100000, 999999)

        if kind == "delivery":
            brand = random.choice(DELIVERY)
            dom = LEGIT_PORTAL["delivery"]
            url = f"https://{dom}/track/{ref}"
            body = (
                f"Hi,\n\nYour parcel tracking has been updated.\n"
                f"Tracking number: {ref}\n\nThanks,\n{brand} Notifications"
            )
            use_attachment = _maybe(0.35)  # legit sometimes attach PDFs
            if use_attachment:
                att = f"Delivery_Notice_{ref}.pdf"
                e = dict(
                    sender_name=f"{brand} Notifications",
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: Tracking update ({ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="delivery",
                    links=[],
                    attachments=[att],
                )
            else:
                e = dict(
                    sender_name=f"{brand} Notifications",
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: Tracking update ({ref})",
                    body=_format_body_with_optional_url(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="delivery",
                    links=[url],
                    attachments=[],
                )
            return _ensure_xor_links_attachments(e)

        if kind == "cloud":
            brand = random.choice(CLOUD)
            dom = LEGIT_PORTAL["cloud"]
            doc = random.choice(["Policy_Update.pdf", "Meeting_Notes.pdf", "Project_Brief.pdf", "Budget_Summary.pdf"])
            url = f"https://{dom}/files/view/{_slug(doc)}?ref={ref}"
            body = f"A file has been shared with you.\n\nFile: {doc}\n\nThanks,\n{brand}"
            if _maybe(0.25):
                # legit attachment share notification (invite/receipt style)
                att = f"Share_Receipt_{ref}.pdf"
                e = dict(
                    sender_name=brand,
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: File shared with you (Ref {ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="cloud",
                    links=[],
                    attachments=[att],
                )
            else:
                e = dict(
                    sender_name=brand,
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: File shared with you (Ref {ref})",
                    body=_format_body_with_optional_url(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="cloud",
                    links=[url],
                    attachments=[],
                )
            return _ensure_xor_links_attachments(e)

        if kind == "membership":
            org = random.choice(ORGS)
            dom = LEGIT_PORTAL["membership"]
            url = f"https://{dom}/{_slug(org)}/account"
            body = f"Hi,\n\nYour {org} membership is active.\n\nThanks,\n{org}"
            if _maybe(0.30):
                att = f"{org}_Welcome_{ref}.pdf"
                e = dict(
                    sender_name=org,
                    sender_email=f"noreply@{dom}",
                    subject=f"Welcome to {org} — membership active (Ref {ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="subscription",
                    links=[],
                    attachments=[att],
                )
            else:
                e = dict(
                    sender_name=org,
                    sender_email=f"noreply@{dom}",
                    subject=f"Welcome to {org} — membership active (Ref {ref})",
                    body=_format_body_with_optional_url(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="subscription",
                    links=[url],
                    attachments=[],
                )
            return _ensure_xor_links_attachments(e)

        if kind == "uni":
            uni = random.choice(UNIS)
            dom = LEGIT_PORTAL["uni"]
            url = f"https://{dom}/portal/timetable?week={random.randint(1, 12)}"
            body = f"Hi,\n\nYour timetable has been updated. Please check the student portal.\n\nRegistry"
            if _maybe(0.30):
                att = f"Timetable_Summary_{ref}.pdf"
                e = dict(
                    sender_name=f"{uni} Registry",
                    sender_email=f"registry@{dom}",
                    subject="Timetable update available",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="education",
                    links=[],
                    attachments=[att],
                )
            else:
                e = dict(
                    sender_name=f"{uni} Registry",
                    sender_email=f"registry@{dom}",
                    subject="Timetable update available",
                    body=_format_body_with_optional_url(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="education",
                    links=[url],
                    attachments=[],
                )
            return _ensure_xor_links_attachments(e)

        # invoice (legit attachment)
        vendor = random.choice(["BrightCables Ltd", "Westridge Supplies", "Greenlight Maintenance", "OfficeMart"])
        dom = f"{_slug(vendor).replace('-ltd','')}.co.uk"
        inv = f"INV-{random.randint(10000, 99999)}"
        body = (
            f"Hello,\n\nPlease find attached invoice {inv}.\n"
            "If you have any questions, reply to this email.\n\nThanks,\nAccounts"
        )
        e = dict(
            sender_name=f"{vendor} Accounts",
            sender_email=f"accounts@{dom}",
            subject=f"Invoice attached: {inv}",
            body=body,
            is_phish=False,
            difficulty=diff,
            category="billing",
            links=[],
            attachments=[f"{inv}.pdf"],
        )
        return _ensure_xor_links_attachments(e)

    def _make_phish_email(diff: int) -> Dict[str, Any]:
        diff = _clamp_difficulty(diff)
        kind = random.choice(["bank", "delivery", "cloud", "account", "invoice"])
        ref = random.randint(100000, 999999)

        # Common phish “infra”
        evil_root = random.choice([
            "account-security-alerts.com",
            "secure-authentication.co",
            "portal-verification.com",
            "service-login.co",
            "customer-support-portal.com",
        ])

        # Difficulty-dependent tone
        if diff == 1:
            urgency = "IMMEDIATELY!!!"
        elif diff == 2:
            urgency = "within 24 hours"
        elif diff == 3:
            urgency = "as soon as possible"
        elif diff == 4:
            urgency = "at your earliest convenience"
        else:
            urgency = "today"

        # --- BANK ---
        if kind == "bank":
            bank = random.choice(BANKS)
            legit_dom = LEGIT_PORTAL["bank"]
            look = _lookalike_domain(legit_dom, diff)

            subject = f"{bank}: unusual login attempt detected (Case {ref})"
            if diff <= 2:
                subject = f"URGENT: {bank} Unusual Login attempt Detected"

            # Link strategy
            if diff == 5:
                url = _userinfo_trick(legit_dom, evil_root, f"verify/session/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/secure/{bank.lower()}/review/{ref}"
            elif diff == 3:
                url = f"https://{look}/login/review/{ref}"
            elif diff == 2:
                url = f"http://{look}/verify"
            else:
                url = _bad_url_variants(f"https://{look}/verify-now")

            body = (
                f"Dear customer,\n\n"
                f"We detected a sign-in attempt that may not have been you.\n"
                f"If you did not request this, secure your account {urgency}.\n"
            )
            e = dict(
                sender_name=f"{bank} Security",
                sender_email=f"security@{look}",
                subject=subject,
                body=_format_body_with_optional_url(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="banking",
                links=[url],
                attachments=[],
            )
            return _ensure_xor_links_attachments(e)

        # --- DELIVERY ---
        if kind == "delivery":
            carrier = random.choice(DELIVERY)
            legit_dom = LEGIT_PORTAL["delivery"]
            look = _lookalike_domain(legit_dom, diff)
            subject = f"{carrier}: delivery issue — action required"

            if diff == 5:
                url = _userinfo_trick(legit_dom, evil_root, f"reschedule/{ref}")
            elif diff == 4:
                # Subdomain bait: looks like carrier portal
                url = f"https://delivery.{legit_dom}.{evil_root}/slot/{ref}"
            elif diff == 3:
                url = f"https://{look}/reschedule/{ref}"
            elif diff == 2:
                url = f"http://{look}/confirm-slot"
            else:
                url = _bad_url_variants(f"https://{look}/reschedule")

            body = (
                "We attempted delivery but couldn't complete it.\n"
                f"Please confirm a new delivery slot {urgency} to avoid return.\n"
            )
            e = dict(
                sender_name=f"{carrier} Notifications",
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=_format_body_with_optional_url(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="delivery",
                links=[url],
                attachments=[],
            )
            return _ensure_xor_links_attachments(e)

        # --- CLOUD DOC SHARE ---
        if kind == "cloud":
            brand = random.choice(CLOUD)
            legit_dom = LEGIT_PORTAL["cloud"]
            look = _lookalike_domain(legit_dom, diff)
            doc = random.choice(["Shared_Document.pdf", "Policy_Update.pdf", "AccessReview_Q1.xlsx", "Invoice_Copy.pdf"])

            subject = f"{brand}: shared document"
            if diff <= 2:
                subject = f"{brand} - Shared file requires login"

            if diff == 5:
                url = _userinfo_trick(legit_dom, evil_root, f"doc/open/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/s/{ref}/open"
            elif diff == 3:
                url = f"https://{look}/doc/open?id={ref}"
            elif diff == 2:
                url = f"http://{look}/open?id={ref}"
            else:
                url = _bad_url_variants(f"https://{look}/open?id={ref}")

            body = (
                f"A document has been shared with you.\n"
                f"File: {doc}\n"
                f"Sign in to view.\n"
            )
            e = dict(
                sender_name=brand,
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=_format_body_with_optional_url(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="cloud",
                links=[url],
                attachments=[],
            )
            return _ensure_xor_links_attachments(e)

        # --- ACCOUNT LOCK (marketplace / SaaS) ---
        if kind == "account":
            brand = random.choice(MARKET + CLOUD)
            legit_dom = LEGIT_PORTAL["market"]
            look = _lookalike_domain(legit_dom, diff)
            subject = f"{brand}: account security notice (Ref {ref})"
            if diff <= 2:
                subject = f"{brand} ACCOUNT LOCKED - VERIFY NOW"

            if diff == 5:
                url = _userinfo_trick(legit_dom, evil_root, f"restore/{brand.lower()}/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/account/restore/{ref}"
            elif diff == 3:
                url = f"https://{look}/restore/{ref}"
            elif diff == 2:
                url = f"http://{look}/verify"
            else:
                url = _bad_url_variants(f"https://{look}/verify")

            body = (
                "We detected activity that requires verification.\n"
                f"To avoid restricted access, confirm your details {urgency}.\n"
            )
            e = dict(
                sender_name=f"{brand} Support",
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=_format_body_with_optional_url(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="account",
                links=[url],
                attachments=[],
            )
            return _ensure_xor_links_attachments(e)

        # --- INVOICE (attachment-based phish) ---
        vendor = random.choice(["BrightCables", "OfficeMart", "Greenlight", "Westridge"])
        inv = f"INV-{random.randint(10000, 99999)}"
        # At high diff, sender can look legit-ish, attachment looks clean
        if diff >= 4:
            sender_dom = f"{_slug(vendor)}.co.uk"
        else:
            sender_dom = f"{_slug(vendor)}-billing.co"

        subject = f"Invoice attached: {inv}"
        if diff <= 2:
            subject = f"OVERDUE {inv}!!! OPEN ATTACHMENT"

        body = (
            f"Hello,\n\nPlease see attached invoice {inv}.\n"
            "Let us know once scheduled.\n\nThanks,\nAccounts"
        )

        att = _attachment_for(diff, kind="invoice", is_phish=True)
        e = dict(
            sender_name=f"{vendor} Accounts",
            sender_email=f"accounts@{sender_dom}",
            subject=subject,
            body=body,
            is_phish=True,
            difficulty=diff,
            category="billing",
            links=[],
            attachments=[att],
        )
        return _ensure_xor_links_attachments(e)

    # ---- Build pool with strong per-difficulty coverage ----
    # 20 per diff: 10 legit + 10 phish
    for diff in range(1, 6):
        for _ in range(10):
            emails.append(_make_legit_email(diff))
        for _ in range(10):
            emails.append(_make_phish_email(diff))

    # Extra diff=5 spear-ish “thread hijack” style (still XOR)
    # These are polished, not shouty, and use tricky URLs or clean PDFs.
    for _ in range(10):
        real_dom = LEGIT_PORTAL["bank"]
        evil_dom = random.choice(["login-review.co", "secure-casework.com", "identity-checks.co"])
        ref = random.randint(100000, 999999)

        if _maybe(0.5):
            # link spear: userinfo trick
            url = _userinfo_trick(real_dom, evil_dom, f"case/{ref}/review")
            body = (
                "Hi,\n\n"
                "Following up on the security review opened for your account.\n"
                "Please confirm you recognise the sign-in record.\n\n"
                "Thanks,\nSecurity Operations"
            )
            emails.append(_ensure_xor_links_attachments(dict(
                sender_name="Security Operations",
                sender_email=f"soc@{real_dom}",  # looks legit
                subject="Security review follow-up",
                body=_format_body_with_optional_url(5, body, url),
                is_phish=True,
                difficulty=5,
                category="security",
                links=[url],
                attachments=[],
            )))
        else:
            # attachment spear: clean PDF name
            att = _attachment_for(5, kind="invoice", is_phish=True)
            body = (
                "Hi,\n\n"
                "Attached is the confirmation document requested for today.\n"
                "If anything is incorrect, reply and we’ll amend it.\n\n"
                "Thanks,\nAccounts"
            )
            emails.append(_ensure_xor_links_attachments(dict(
                sender_name="Accounts Team",
                sender_email=f"accounts@{real_dom}",  # looks legit
                subject="Confirmation document attached",
                body=body,
                is_phish=True,
                difficulty=5,
                category="spearphish",
                links=[],
                attachments=[att]
            )))

    random.shuffle(emails)
    return emails

def _slug(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("'", "")
        .replace("  ", " ")
        .strip()
        .replace(" ", "-")
    )


def _domain(company_name: str) -> str:
    return f"{_slug(company_name)}.co.uk"


def _curated_levels_first5(scenario_by_company: dict[str, Scenario]):
    nb = scenario_by_company["Northbridge Utilities"]
    hl = scenario_by_company["Harbourline Logistics"]
    ch = scenario_by_company["Crestview Health Partners"]

    # Helper to clean manager names for email addresses
    def clean_mgr_name(name: str) -> str:
        return name.replace(".", "").replace(",", "").lower().replace(" ", ".")

    nb_domain = _domain(nb.company_name)
    hl_domain = _domain(hl.company_name)
    ch_domain = _domain(ch.company_name)

    # lookalike domains (easy cues)
    nb_phish = "northbridge-utilities-payments.com"
    nb_spoof = "northbridge-utilities-sharepoint.com"
    hl_phish = "harbourline-logistics-verify.com"
    hl_track = "harbourline-delivery-tracking.com"
    ch_phish = "crestview-payroll-secure.com"

    # Each level: title/briefing + ordered emails.
    # RULE: exactly one of links/attachments must be non-empty.
    return [
        dict(
            scenario=nb,
            number=1,
            title="Accounts Payable basics",
            briefing="You're new in Accounts Payable. Expect invoices, POs, and supplier queries.",
            emails=[
                dict(
                    sender_name="Procurement Team",
                    sender_email=f"procurement@{nb_domain}",
                    subject="PO 48391 approved (PDF attached)",
                    body="Hi,\n\nPO 48391 has been approved. Please match any incoming invoices to this PO.\n\nThanks,\nProcurement",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["PO_48391.pdf"],
                ),
                dict(
                    sender_name="Invoice Processing",
                    sender_email=f"invoices@{nb_domain}",
                    subject="New invoice received: INV-20419",
                    body="Hi,\n\nNew supplier invoice received. Please review and process within 3 working days.\n\nRegards,\nInvoice Processing",
                    is_phish=False,
                    difficulty=1,
                    category="finance",
                    links=[],
                    attachments=["INV-20419.pdf"],
                ),
                dict(
                    sender_name=nb.line_manager_name,
                    sender_email=f"{clean_mgr_name(nb.line_manager_name)}@{nb_domain}",
                    subject="Quick check: supplier chasing payment",
                    body=f"Hi,\n\nCan you confirm if Westridge Supplies was paid this week?\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/suppliers/westridge"],
                    attachments=[],
                ),
                dict(
                    sender_name="Supplier Payments",
                    sender_email=f"payments@{nb_phish}",
                    subject="URGENT: payment failed — re-authorise TODAY",
                    body="Hello,\n\nPayment failed. Re-authorise today to avoid service interruption.\n\nRe-authorise:\n"
                    f"http://{nb_phish}/reauthorise\n",
                    is_phish=True,
                    difficulty=1,
                    category="phish",
                    links=[f"http://{nb_phish}/reauthorise"],
                    attachments=[],
                ),
                dict(
                    sender_name="Voice Mail",
                    sender_email=f"voicemail@{nb_phish}",
                    subject="New voice message (open attachment)",
                    body="You received a new voice message.\n\nOpen the attached file to listen.",
                    is_phish=True,
                    difficulty=1,
                    category="phish",
                    links=[],
                    attachments=["voice_message.htm"],
                ),
            ],
        ),
        dict(
            scenario=nb,
            number=2,
            title="Supplier changes and shared docs",
            briefing="More supplier comms and shared files. Watch for fake portals.",
            emails=[
                dict(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Supplier master data: update request (internal form)",
                    body="Hi,\n\nCan you review the supplier master data update requests in the portal?\n\nThanks,\nAccounts",
                    is_phish=False,
                    difficulty=1,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/supplier-master/requests"],
                    attachments=[],
                ),
                dict(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="Invoice copy requested (attached)",
                    body="Hello,\n\nAs requested, attached is the invoice copy.\n\nThank you,\nBilling",
                    is_phish=False,
                    difficulty=1,
                    category="supplier",
                    links=[],
                    attachments=["INV-20311.pdf"],
                ),
                dict(
                    sender_name=f"{nb.company_name} SharePoint",
                    sender_email=f"no-reply@{nb_spoof}",
                    subject="Shared file: Supplier_BankChange_Form.pdf",
                    body="A document has been shared with you.\n\nOpen document:\n"
                    f"http://{nb_spoof}/open?id=92831\n",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[f"http://{nb_spoof}/open?id=92831"],
                    attachments=[],
                ),
                dict(
                    sender_name="Supplier Billing",
                    sender_email=f"billing@{nb_phish}",
                    subject="Bank details form (attached)",
                    body="Hello,\n\nPlease complete the attached bank details form today.\n\nRegards,\nBilling",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[],
                    attachments=["BankDetailsForm.pdf.exe"],
                ),
                dict(
                    sender_name="Procurement Team",
                    sender_email=f"procurement@{nb_domain}",
                    subject="Approved supplier list (Q1)",
                    body="Hi,\n\nAttached is the approved supplier list for Q1.\n\nThanks,\nProcurement",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["Approved_Suppliers_Q1.pdf"],
                ),
            ],
        ),
        dict(
            scenario=hl,
            number=3,
            title="Procurement: quotes and onboarding",
            briefing="You manage quotes and suppliers. Be wary of vendor verification pressure.",
            emails=[
                dict(
                    sender_name="Operations",
                    sender_email=f"operations@{hl_domain}",
                    subject="Request: quote for pallet wrap (specs attached)",
                    body="Hi,\n\nCan you get a quote for pallet wrap based on the attached spec?\n\nThanks,\nOperations",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["Pallet_Wrap_Spec.pdf"],
                ),
                dict(
                    sender_name="Vendor Onboarding",
                    sender_email=f"onboarding@{hl_domain}",
                    subject="New supplier onboarding checklist",
                    body="Hi,\n\nPlease use the attached checklist for new supplier onboarding.\n\nThanks,\nProcurement Ops",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["Supplier_Onboarding_Checklist.pdf"],
                ),
                dict(
                    sender_name="Harbourline Vendor Portal",
                    sender_email=f"no-reply@{hl_phish}",
                    subject="ACTION REQUIRED: Vendor details verification",
                    body="Your vendor record requires verification.\n\nVerify now:\n"
                    f"http://{hl_phish}/vendor/verify\n",
                    is_phish=True,
                    difficulty=1,
                    category="phish",
                    links=[f"http://{hl_phish}/vendor/verify"],
                    attachments=[],
                ),
                dict(
                    sender_name="Supplier Quotes",
                    sender_email="sales@packaging-direct.co.uk",
                    subject="Quote attached: pallet wrap (Ref Q-1182)",
                    body="Hi,\n\nPlease find our quote attached.\n\nKind regards,\nSales",
                    is_phish=False,
                    difficulty=1,
                    category="supplier",
                    links=[],
                    attachments=["Quote_Q-1182.pdf"],
                ),
                dict(
                    sender_name="Packaging Direct",
                    sender_email="sales@packaging-directs.co.uk",
                    subject="Revised quote (open attached urgently)",
                    body="Hi,\n\nRevised quote attached, please open and approve today.\n\nThanks",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[],
                    attachments=["Quote_1182.xlsm"],
                ),
            ],
        ),
        dict(
            scenario=hl,
            number=4,
            title="Deliveries and customs paperwork",
            briefing="More delivery comms. Watch for fake tracking pages and weird attachments.",
            emails=[
                dict(
                    sender_name="Inbound Logistics",
                    sender_email=f"inbound@{hl_domain}",
                    subject="Container ETA update (see portal link)",
                    body="Hi,\n\nUpdated container ETA is available in the logistics portal.\n\nThanks,\nInbound",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[f"https://{hl_domain}/logistics/eta"],
                    attachments=[],
                ),
                dict(
                    sender_name="Supplier: SteelCo",
                    sender_email="dispatch@steelco.co.uk",
                    subject="Delivery note attached (DN-55219)",
                    body="Hi,\n\nDelivery note attached.\n\nRegards,\nDispatch",
                    is_phish=False,
                    difficulty=1,
                    category="supplier",
                    links=[],
                    attachments=["DN-55219.pdf"],
                ),
                dict(
                    sender_name="Courier Updates",
                    sender_email=f"no-reply@{hl_track}",
                    subject="Delivery delayed — confirm slot",
                    body="Your delivery slot needs confirmation.\n\nConfirm here:\n"
                    f"http://{hl_track}/confirm-slot\n",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[f"http://{hl_track}/confirm-slot"],
                    attachments=[],
                ),
                dict(
                    sender_name="Customs Paperwork",
                    sender_email=f"customs@{hl_phish}",
                    subject="Customs invoice attached - action required",
                    body="Customs invoice attached. Please open and confirm details.",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[],
                    attachments=["CustomsInvoice_55219.pdf.scr"],
                ),
                dict(
                    sender_name="Procurement System",
                    sender_email=f"no-reply@{hl_domain}",
                    subject="PO created: PO-77104 (PDF)",
                    body="A new purchase order has been created. PDF attached for your records.",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["PO-77104.pdf"],
                ),
            ],
        ),
        dict(
            scenario=ch,
            number=5,
            title="HR: onboarding and payroll requests",
            briefing="You coordinate onboarding. Be cautious with payroll and secure forms.",
            emails=[
                dict(
                    sender_name="Recruitment",
                    sender_email=f"recruitment@{ch_domain}",
                    subject="Candidate CV attached (Band 4 Admin)",
                    body="Hi,\n\nCandidate CV attached for review ahead of interview scheduling.\n\nThanks,\nRecruitment",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["CV_Band4_Admin.pdf"],
                ),
                dict(
                    sender_name=ch.line_manager_name,
                    sender_email=f"{clean_mgr_name(ch.line_manager_name)}@{ch_domain}",
                    subject="Onboarding checklist (portal link)",
                    body=f"Hi,\n\nCan you run through the onboarding checklist in the HR portal for the new starter?\n\nThanks,\n{ch.line_manager_name}",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[f"https://{ch_domain}/hr/onboarding/checklist"],
                    attachments=[],
                ),
                dict(
                    sender_name="Payroll Team",
                    sender_email=f"payroll@{ch_phish}",
                    subject="IMPORTANT: Update your payroll details",
                    body="Hi,\n\nWe need you to update payroll details to avoid a missed payment.\n\nUpdate here:\n"
                    f"http://{ch_phish}/update\n",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[f"http://{ch_phish}/update"],
                    attachments=[],
                ),
                dict(
                    sender_name="Internal Comms",
                    sender_email=f"comms@{ch_phish}",
                    subject="New policy document (attached) - read today",
                    body="Please read the attached policy update today and confirm completion.",
                    is_phish=True,
                    difficulty=2,
                    category="phish",
                    links=[],
                    attachments=["Policy_Update_2026.pdf.exe"],
                ),
                dict(
                    sender_name="IT Helpdesk",
                    sender_email=f"it-support@{ch_domain}",
                    subject="New starter account setup (instructions attached)",
                    body="Hi,\n\nAttached are the steps for new starter account setup.\n\nThanks,\nIT",
                    is_phish=False,
                    difficulty=1,
                    category="internal",
                    links=[],
                    attachments=["NewStarter_AccountSetup.pdf"],
                ),
            ],
        ),
    ]


def _curated_levels_6_7(scenario_by_company: dict[str, Scenario]):
    """
    Curated mid/high complexity levels (6–7).
    Keep these deterministic: no random, no sampling.
    """
    nb = scenario_by_company["Northbridge Utilities"]

    def clean_mgr_name(name: str) -> str:
        return name.replace(".", "").replace(",", "").lower().replace(" ", ".")

    nb_domain = _domain(nb.company_name)
    mgr_email = f"{clean_mgr_name(nb.line_manager_name)}@{nb_domain}"

    # Attacker infra consistent with later levels
    nb_vendor_lookalike = "westridge-supplies.co"
    nb_sharepoint_spoof = "northbridge-utilities-sharepoint.com"
    nb_bank_portal_spoof = "northbridge-utilities-payments.com"
    nb_support_spoof = "northbridge-utilities-helpdesk.com"

    def e(**kwargs):
        return dict(**kwargs)

    return [
        # -----------------------------
        # LEVEL 6 — External contacts + process adherence
        # -----------------------------
        dict(
            scenario=nb,
            number=6,
            title="External contacts: approvals, quotes, and a subtle redirect",
            briefing=(
                "Email volume increases. You'll handle supplier quotes, approvals, and a subtle attempt "
                "to redirect a payment-related workflow outside of policy."
            ),
            base_emails=[
                e(
                    sender_name="Procurement Team",
                    sender_email=f"procurement@{nb_domain}",
                    subject="New supplier quote received (PDF attached) — review needed",
                    body="Hi,\n\nAttached is a quote from BrightCables for a Q1 order. Please sanity check totals before we raise PO.\n\nThanks,\nProcurement",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[],
                    attachments=["BrightCables_Quote_Q1.pdf"],
                ),
                e(
                    sender_name="BrightCables Ltd",
                    sender_email="accounts@brightcables.co.uk",
                    subject="RE: Quote Q1 — revised quote attached",
                    body="Hi,\n\nAs discussed, revised quote attached.\n\nKind regards,\nAccounts",
                    is_phish=False,
                    difficulty=3,
                    category="supplier",
                    links=[],
                    attachments=["BrightCables_Quote_Q1_Revised.pdf"],
                ),
                e(
                    sender_name=nb.line_manager_name,
                    sender_email=mgr_email,
                    subject="Can you log today’s supplier comms in the portal? (link)",
                    body=f"Hi,\n\nCan you log today’s supplier comms in the finance portal notes for audit trail?\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/notes"],
                    attachments=[],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_domain}",
                    subject="Reminder: bank changes require verification (policy PDF attached)",
                    body="Hi,\n\nReminder that supplier bank changes must be verified via approved process.\n\nThanks,\nPayments Desk",
                    is_phish=False,
                    difficulty=3,
                    category="finance",
                    links=[],
                    attachments=["Supplier_BankChange_Policy.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: INV-20311 — remittance advice request (PDF attached)",
                    body="Hello,\n\nCould you send remittance advice once payment is scheduled? Attached statement for reference.\n\nThanks,\nBilling",
                    is_phish=False,
                    difficulty=3,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_Statement_Current.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="RE: INV-20311 — updated remittance portal (login)",
                    body=(
                        "Hello,\n\nWe have moved remittance advice to the new portal.\n"
                        "Login to view the message thread:\n"
                        f"http://{nb_bank_portal_spoof}/remittance/login\n"
                    ),
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/remittance/login"],
                    attachments=[],
                ),
                e(
                    sender_name="IT Helpdesk",
                    sender_email=f"it@{nb_domain}",
                    subject="Scheduled maintenance: finance portal (status link)",
                    body="Hi,\n\nPlanned maintenance tonight. Track updates on the status page.\n\nIT",
                    is_phish=False,
                    difficulty=3,
                    category="it",
                    links=[f"https://{nb_domain}/it/status"],
                    attachments=[],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Shared: Supplier_Remittance_Template.xlsx (open link)",
                    body=f"A file has been shared with you.\n\nOpen:\nhttp://{nb_sharepoint_spoof}/open?id=remit-template\n",
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=remit-template"],
                    attachments=[],
                ),
            ],
            wave_emails=[
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Follow-up: payment queue updated (portal)",
                    body="Hi,\n\nPayment queue updated after late approvals. Please re-check before close.\n\nAccounts",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/approvals?late=1"],
                    attachments=[],
                ),
                e(
                    sender_name="Supplier Portal Support",
                    sender_email=f"support@{nb_support_spoof}",
                    subject="Account alert: verify to avoid suspension",
                    body=f"Unusual login attempts detected.\nVerify now:\nhttp://{nb_support_spoof}/verify\n",
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_support_spoof}/verify"],
                    attachments=[],
                ),
            ],
        ),

        # -----------------------------
        # LEVEL 7 — Controls + escalation practice
        # -----------------------------
        dict(
            scenario=nb,
            number=7,
            title="Controls: escalation, evidence, and thread hygiene",
            briefing=(
                "You’ll get conflicting signals. Some legitimate messages are imperfect. "
                "Your goal is to follow process, escalate appropriately, and document decisions."
            ),
            base_emails=[
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Audit request: evidence for 2 invoices (PDF attached)",
                    body="Hi,\n\nPlease provide evidence trail for the attached invoice list by end of day.\n\nThanks,\nAudit",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[],
                    attachments=["Audit_Request_Invoices.pdf"],
                ),
                e(
                    sender_name="Invoice Processing",
                    sender_email=f"invoices@{nb_domain}",
                    subject="Invoice received: INV-20902 (PDF attached)",
                    body="Hi,\n\nInvoice attached. Please process.\n\nInvoice Processing",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[],
                    attachments=["INV-20902.pdf"],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_domain}",
                    subject="Payment exception: supplier bank details mismatch (portal)",
                    body="Hi,\n\nSupplier bank details mismatch flagged. Review exception notes in the portal.\n\nPayments",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/exceptions/last"],
                    attachments=[],
                ),
                e(
                    sender_name=nb.line_manager_name,
                    sender_email=mgr_email,
                    subject="If anything looks off, escalate before actioning (portal link)",
                    body=f"Hi,\n\nIf anything looks off today, escalate before actioning. Log decisions in portal notes.\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/notes"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="INV-20311 — bank confirmation form attached (sign & return)",
                    body="Hello,\n\nAttached bank confirmation form. Please sign and return today.\n\nBilling",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[],
                    attachments=["Westridge_BankConfirmation.pdf.exe"],
                ),
                e(
                    sender_name="IT Security",
                    sender_email=f"security@{nb_domain}",
                    subject="Security bulletin: supplier impersonation examples (PDF attached)",
                    body="Hi,\n\nAttached bulletin with examples of supplier impersonation and what to check.\n\nSecurity",
                    is_phish=False,
                    difficulty=4,
                    category="security",
                    links=[],
                    attachments=["Security_Bulletin_SupplierImpersonation.pdf"],
                ),
                e(
                    sender_name="Supplier Portal",
                    sender_email=f"no-reply@{nb_bank_portal_spoof}",
                    subject="Secure message: action required to view supplier note",
                    body=f"A supplier sent you a secure message.\nLogin:\nhttp://{nb_bank_portal_spoof}/login\n",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/login"],
                    attachments=[],
                ),
            ],
            wave_emails=[
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Escalation: exception queue needs clearing (portal)",
                    body="Hi,\n\nPlease clear what you can from the exception queue before 15:00.\n\nAccounts",
                    is_phish=False,
                    difficulty=5,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/exceptions"],
                    attachments=[],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Shared: Evidence_Pack_Instructions.pdf (open)",
                    body=f"Open:\nhttp://{nb_sharepoint_spoof}/open?id=evidence-pack\n",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=evidence-pack"],
                    attachments=[],
                ),
            ],
        ),
    ]

def _curated_levels_8_10(scenario_by_company: dict[str, Scenario]):
    """
    Curated high-complexity levels (8–10) with timed "wave" emails.
    Wave emails are identified by sort_order >= 100 (no schema changes needed).
    """
    nb = scenario_by_company["Northbridge Utilities"]

    def clean_mgr_name(name: str) -> str:
        return name.replace(".", "").replace(",", "").lower().replace(" ", ".")

    nb_domain = _domain(nb.company_name)
    mgr_email = f"{clean_mgr_name(nb.line_manager_name)}@{nb_domain}"

    # Lookalikes / attacker infra
    nb_cfo_spoof = "northbridge-utilities-finance.com"
    nb_vendor_lookalike = "westridge-supplies.co"  # subtle TLD
    nb_sharepoint_spoof = "northbridge-utilities-sharepoint.com"
    nb_bank_portal_spoof = "northbridge-utilities-payments.com"
    nb_doc_spoof = "northbridge-utilities-docs.com"
    nb_support_spoof = "northbridge-utilities-helpdesk.com"

    def e(**kwargs):
        # small helper to keep dicts clean
        return dict(**kwargs)

    return [
        # -----------------------------
        # LEVEL 8 — Quarter-end pressure begins
        # -----------------------------
        dict(
            scenario=nb,
            number=8,
            title="Quarter-end close: supplier escalations",
            briefing=(
                "It’s quarter-end close. You’ll see real supplier chasers, internal approvals, "
                "and convincing payment-change requests. Keep your judgement under pressure."
            ),
            base_emails=[
                e(
                    sender_name="Finance Ops",
                    sender_email=f"finance-ops@{nb_domain}",
                    subject="Quarter-end close checklist (portal)",
                    body="Hi,\n\nQuarter-end close is underway. Please work through the checklist in the portal.\n\nThanks,\nFinance Ops",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/checklist"],
                    attachments=[],
                ),
                e(
                    sender_name=nb.line_manager_name,
                    sender_email=mgr_email,
                    subject="Quarter-end: please prioritise vendor chasers today",
                    body=f"Hi,\n\nPlease prioritise vendor chasers today. Flag anything suspicious before actioning.\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/priorities"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: INV-20311 — payment date confirmation (attached statement)",
                    body="Hello,\n\nAttaching statement for INV-20311 and INV-20344. Can you confirm the scheduled payment date?\n\nThanks,\nBilling",
                    is_phish=False,
                    difficulty=3,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_Statement_Q4.pdf"],
                ),
                e(
                    sender_name="Procurement Team",
                    sender_email=f"procurement@{nb_domain}",
                    subject="Approved suppliers — Q4 addendum (PDF)",
                    body="Hi,\n\nAttached is the Q4 addendum to the approved supplier list.\n\nThanks,\nProcurement",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[],
                    attachments=["Approved_Suppliers_Q4_Addendum.pdf"],
                ),
                e(
                    sender_name="Invoice Processing",
                    sender_email=f"invoices@{nb_domain}",
                    subject="Invoice received: INV-20991 (PDF attached)",
                    body="Hi,\n\nNew invoice received. Please process according to policy.\n\nRegards,\nInvoice Processing",
                    is_phish=False,
                    difficulty=3,
                    category="finance",
                    links=[],
                    attachments=["INV-20991.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="RE: INV-20311 — payment failed, re-authorise (portal)",
                    body=(
                        "Hello,\n\nWe attempted to take payment but it failed.\n"
                        "Re-authorise via the secure portal to avoid late fees:\n"
                        f"http://{nb_bank_portal_spoof}/retry?inv=20311\n"
                    ),
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/retry?inv=20311"],
                    attachments=[],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Shared file: Q4_Close_Schedule.xlsx (open link)",
                    body=(
                        "A file has been shared with you.\n\n"
                        "Open document:\n"
                        f"http://{nb_sharepoint_spoof}/open?id=Q4Close\n"
                    ),
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=Q4Close"],
                    attachments=[],
                ),
                e(
                    sender_name="IT Status",
                    sender_email=f"it-status@{nb_domain}",
                    subject="Notice: Finance portal performance issues (status page)",
                    body="Hi,\n\nWe’re investigating intermittent slowness on the finance portal. Track updates here.\n\nIT",
                    is_phish=False,
                    difficulty=3,
                    category="it",
                    links=[f"https://{nb_domain}/it/status/finance-portal"],
                    attachments=[],
                ),
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Payment run: approvals needed (portal)",
                    body="Hi,\n\nPayment run approvals needed before 16:00. Please review the queue.\n\nThanks,\nAccounts",
                    is_phish=False,
                    difficulty=3,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/approvals"],
                    attachments=[],
                ),
                e(
                    sender_name="Supplier Onboarding",
                    sender_email=f"onboarding@{nb_domain}",
                    subject="New supplier request: Westbridge Renewables (PDF pack)",
                    body="Hi,\n\nAttached is the supplier request pack for Westbridge Renewables.\n\nThanks,\nOnboarding",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[],
                    attachments=["Supplier_Request_WestbridgeRenewables.pdf"],
                ),
                e(
                    sender_name="Westbridge Renewables",
                    sender_email="ap@westbridgerenewables.co.uk",
                    subject="Bank details letter (PDF attached)",
                    body="Hello,\n\nPlease find attached our bank details letter for your vendor setup.\n\nRegards,\nAP",
                    is_phish=False,
                    difficulty=3,
                    category="supplier",
                    links=[],
                    attachments=["Westbridge_BankDetailsLetter.pdf"],
                ),
                e(
                    sender_name="Westbridge Renewables",
                    sender_email="ap@westbridge-renewables.co",  # subtle domain mismatch
                    subject="Bank change confirmation required (open portal)",
                    body=(
                        "Hello,\n\nTo complete setup, confirm bank details in the secure portal:\n"
                        f"http://{nb_bank_portal_spoof}/vendor/confirm?wb=1\n"
                    ),
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/vendor/confirm?wb=1"],
                    attachments=[],
                ),
                e(
                    sender_name="Finance Shared Drive",
                    sender_email=f"no-reply@{nb_doc_spoof}",
                    subject="Document: Vendor_Master_Update.xlsm (download)",
                    body=(
                        "A document has been shared with you.\n"
                        "Download:\n"
                        f"http://{nb_doc_spoof}/download?v=master\n"
                    ),
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/download?v=master"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Quarter-end sample: provide invoice trail (PDF guidance attached)",
                    body="Hi,\n\nPlease see attached guidance for audit sample requests. No action needed yet.\n\nThanks,\nInternal Audit",
                    is_phish=False,
                    difficulty=3,
                    category="internal",
                    links=[],
                    attachments=["Audit_Sample_Guidance.pdf"],
                ),
                e(
                    sender_name="Voice Mail",
                    sender_email=f"voicemail@{nb_support_spoof}",
                    subject="New voicemail received (open attachment)",
                    body="You received a voicemail.\n\nOpen the attachment to listen.",
                    is_phish=True,
                    difficulty=4,
                    category="phish",
                    links=[],
                    attachments=["Voicemail_84291.htm"],
                ),
            ],
            wave_emails=[
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="FOLLOW-UP: payment run reopened (portal)",
                    body="Hi,\n\nWe reopened the payment run due to late approvals. Please re-check approvals.\n\nThanks,\nAccounts",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/approvals?reopen=1"],
                    attachments=[],
                ),
                e(
                    sender_name="CFO Office",
                    sender_email=f"cfo@{nb_cfo_spoof}",
                    subject="Urgent: settle supplier today — confirm via link",
                    body=(
                        "Hi,\n\nNeed this supplier settled today before close. Confirm you can action via the link:\n"
                        f"http://{nb_cfo_spoof}/confirm?action=pay\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_cfo_spoof}/confirm?action=pay"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: INV-20344 — remittance advice request (attached)",
                    body="Hello,\n\nCould you send remittance advice once payment is scheduled? Attached statement for reference.\n\nThanks,\nBilling",
                    is_phish=False,
                    difficulty=4,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_Statement_Supplement.pdf"],
                ),
                e(
                    sender_name="IT Helpdesk",
                    sender_email=f"it@{nb_domain}",
                    subject="Reminder: do not approve bank changes via email (policy PDF)",
                    body="Hi,\n\nReminder: bank changes must be verified via approved process. See attached.\n\nIT",
                    is_phish=False,
                    difficulty=4,
                    category="it",
                    links=[],
                    attachments=["BankChange_Verification_Policy.pdf"],
                ),
                e(
                    sender_name="Supplier Portal",
                    sender_email=f"no-reply@{nb_bank_portal_spoof}",
                    subject="Action required: secure login to view supplier message",
                    body=(
                        "A supplier sent you a message.\n"
                        "Secure login:\n"
                        f"http://{nb_bank_portal_spoof}/login\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/login"],
                    attachments=[],
                ),
            ],
        ),

        # -----------------------------
        # LEVEL 9 — Conflicting authority & thread pressure
        # -----------------------------
        dict(
            scenario=nb,
            number=9,
            title="Authority conflict: payment redirect & escalation",
            briefing=(
                "Conflicting instructions arrive mid-stream (vendor vs internal vs exec). "
                "Some legit messages are messy; some phish are polished."
            ),
            base_emails=[
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Payment exception queue (portal)",
                    body="Hi,\n\nPlease review the payment exception queue and clear what you can before noon.\n\nThanks,\nAccounts",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/exceptions"],
                    attachments=[],
                ),
                e(
                    sender_name="Procurement Team",
                    sender_email=f"procurement@{nb_domain}",
                    subject="Supplier onboarding: required docs missing (PDF attached)",
                    body="Hi,\n\nWe’re missing docs for a supplier. See attached checklist and chase if needed.\n\nThanks,\nProcurement",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[],
                    attachments=["Supplier_Documents_Checklist.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: INV-20311 — please confirm remittance method",
                    body="Hello,\n\nHow will remittance advice be sent? Portal or email? Please confirm.\n\nThanks,\nBilling",
                    is_phish=False,
                    difficulty=4,
                    category="supplier",
                    links=[f"https://{nb_domain}/finance/remittance/options"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="RE: INV-20311 — updated remittance portal (login)",
                    body=(
                        "Hello,\n\nWe’ve moved remittance to the new portal. Login below:\n"
                        f"http://{nb_doc_spoof}/remit/login\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/remit/login"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Audit sample request #2 (PDF attached)",
                    body="Hi,\n\nPlease see attached audit sample request list. Provide documents by end of day.\n\nThanks,\nAudit",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[],
                    attachments=["Audit_Sample_Request_2.pdf"],
                ),
                e(
                    sender_name="Finance Ops",
                    sender_email=f"finance-ops@{nb_domain}",
                    subject="Close timetable update (portal)",
                    body="Hi,\n\nTimetable update posted in the close portal.\n\nFinance Ops",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/timetable"],
                    attachments=[],
                ),
                e(
                    sender_name="CEO Assistant",
                    sender_email=f"ea@{nb_domain}",
                    subject="Request: priority supplier settlement list (PDF attached)",
                    body="Hi,\n\nCEO requested the list of priority supplier settlements. Attached template.\n\nThanks,\nEA",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[],
                    attachments=["Priority_Settlement_Template.pdf"],
                ),
                e(
                    sender_name="CFO Office",
                    sender_email=f"cfo-office@{nb_domain}",
                    subject="Supplier escalation — do not miss close (portal note)",
                    body="Hi,\n\nEscalation noted. Update status in the portal comment thread.\n\nCFO Office",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/escalations/thread/771"],
                    attachments=[],
                ),
                e(
                    sender_name="CFO",
                    sender_email=f"cfo@{nb_cfo_spoof}",
                    subject="RE: escalation — use updated bank details (secure form)",
                    body=(
                        "Use updated bank details to resolve this today.\n"
                        "Complete the secure form:\n"
                        f"http://{nb_bank_portal_spoof}/secure/bank-change\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/secure/bank-change"],
                    attachments=[],
                ),
                e(
                    sender_name="Invoice Processing",
                    sender_email=f"invoices@{nb_domain}",
                    subject="Invoice received: INV-21004 (PDF attached)",
                    body="Hi,\n\nInvoice attached. Please process.\n\nInvoice Processing",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[],
                    attachments=["INV-21004.pdf"],
                ),
                e(
                    sender_name="Supplier: BrightCables Ltd",
                    sender_email="accounts@brightcables.co.uk",
                    subject="Statement attached (Q4)",
                    body="Hi,\n\nPlease find attached our Q4 statement.\n\nThanks,\nAccounts",
                    is_phish=False,
                    difficulty=4,
                    category="supplier",
                    links=[],
                    attachments=["BrightCables_Q4_Statement.pdf"],
                ),
                e(
                    sender_name="BrightCables Billing",
                    sender_email="accounts@brightcables-billing.co",
                    subject="Overdue: confirm payment via link",
                    body=(
                        "Hello,\n\nOverdue item. Confirm payment now:\n"
                        "http://brightcables-billing.co/pay\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=["http://brightcables-billing.co/pay"],
                    attachments=[],
                ),
                e(
                    sender_name="IT Security",
                    sender_email=f"security@{nb_domain}",
                    subject="Security bulletin: exec spoof attempts rising (PDF attached)",
                    body="Hi,\n\nWe’re seeing exec spoof attempts. See attached bulletin for examples.\n\nSecurity",
                    is_phish=False,
                    difficulty=4,
                    category="security",
                    links=[],
                    attachments=["Security_Bulletin_ExecSpoof.pdf"],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Shared: Remittance_Advice_Exporter.xlsm",
                    body="A file has been shared.\n\nOpen here:\n"
                         f"http://{nb_sharepoint_spoof}/open?id=remit-export\n",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=remit-export"],
                    attachments=[],
                ),
                e(
                    sender_name=nb.line_manager_name,
                    sender_email=mgr_email,
                    subject="Please log decisions clearly (portal)",
                    body=f"Hi,\n\nPlease log what you did + why in the portal notes for audit trail.\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=4,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/notes"],
                    attachments=[],
                ),
                e(
                    sender_name="Supplier Portal Support",
                    sender_email=f"support@{nb_support_spoof}",
                    subject="Your account will be suspended — verify now",
                    body=(
                        "We detected failed logins. Verify your account to prevent suspension:\n"
                        f"http://{nb_support_spoof}/verify\n"
                    ),
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_support_spoof}/verify"],
                    attachments=[],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_domain}",
                    subject="Bank change request received (PDF attached) — do not action without verification",
                    body="Hi,\n\nBank change request received. Attached request. Verify before actioning.\n\nPayments Desk",
                    is_phish=False,
                    difficulty=4,
                    category="finance",
                    links=[],
                    attachments=["BankChange_Request_Westridge.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="BankChange_Request_Westridge.pdf (attached) — sign & return",
                    body="Sign and return today.\n\nBilling",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[],
                    attachments=["BankChange_Request_Westridge.pdf.exe"],
                ),
            ],
            wave_emails=[
                e(
                    sender_name="CFO Office",
                    sender_email=f"cfo-office@{nb_domain}",
                    subject="Update needed: escalation status in thread (portal)",
                    body="Hi,\n\nPlease update the escalation thread with current status.\n\nCFO Office",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/escalations/thread/771?update=1"],
                    attachments=[],
                ),
                e(
                    sender_name="Vendor Compliance",
                    sender_email=f"no-reply@{nb_doc_spoof}",
                    subject="Compliance document pending — open to sign",
                    body="Open to sign:\n"
                         f"http://{nb_doc_spoof}/sign?id=8871\n",
                    is_phish=True,
                    difficulty=5,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/sign?id=8871"],
                    attachments=[],
                ),
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Payment run locked in 20 mins (portal)",
                    body="Hi,\n\nPayment run will lock in 20 mins. Final checks in portal.\n\nAccounts",
                    is_phish=False,
                    difficulty=5,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/final-checks"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Reminder: retain evidence (PDF attached)",
                    body="Hi,\n\nReminder to retain evidence screenshots/documents. See attached.\n\nAudit",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[],
                    attachments=["Evidence_Retention_Guide.pdf"],
                ),
                e(
                    sender_name="CFO",
                    sender_email=f"cfo@{nb_cfo_spoof}",
                    subject="Final instruction — use secure portal now",
                    body=f"Final instruction. Use secure portal:\nhttp://{nb_bank_portal_spoof}/secure/approve\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_bank_portal_spoof}/secure/approve"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: Please ignore prior email — correct remittance address (attached)",
                    body="Sorry — please ignore prior portal link. Attached correct remittance details.\n\nBilling",
                    is_phish=False,
                    difficulty=5,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_Remittance_Details.pdf"],
                ),
            ],
        ),

        # -----------------------------
        # LEVEL 10 — Crisis close day + multiple waves
        # -----------------------------
        dict(
            scenario=nb,
            number=10,
            title="Close day incident: overload + multi-thread attacks",
            briefing=(
                "Close day. Volume spikes. Threads evolve. Some messages attempt to hijack legitimate chains. "
                "Timed emails simulate pressure — stay disciplined."
            ),
            base_emails=[
                e(
                    sender_name="Finance Ops",
                    sender_email=f"finance-ops@{nb_domain}",
                    subject="CLOSE DAY: final timetable (portal)",
                    body="Hi,\n\nFinal timetable posted.\n\nFinance Ops",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/final-timetable"],
                    attachments=[],
                ),
                e(
                    sender_name="IT Status",
                    sender_email=f"it-status@{nb_domain}",
                    subject="Incident: intermittent email delivery delays (status page)",
                    body="Hi,\n\nWe’re investigating email delivery delays. Status updates here.\n\nIT",
                    is_phish=False,
                    difficulty=5,
                    category="it",
                    links=[f"https://{nb_domain}/it/status/email-delays"],
                    attachments=[],
                ),
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Close day: payment run in progress (portal)",
                    body="Hi,\n\nPayment run in progress. Monitor approvals in portal.\n\nAccounts",
                    is_phish=False,
                    difficulty=5,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/run"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Close day audit spot checks (PDF attached)",
                    body="Hi,\n\nSpot checks attached. Please be ready to provide evidence.\n\nAudit",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[],
                    attachments=["CloseDay_Audit_SpotChecks.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="RE: INV-20311 — final chaser before close (attached statement)",
                    body="Hello,\n\nFinal chaser before your close. Attached statement.\n\nBilling",
                    is_phish=False,
                    difficulty=5,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_FinalChaser_Statement.pdf"],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email=f"billing@{nb_vendor_lookalike}",
                    subject="RE: INV-20311 — reply chain update (secure link)",
                    body=f"Reply chain update. View message securely:\nhttp://{nb_doc_spoof}/thread/20311\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/thread/20311"],
                    attachments=[],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Shared: CloseDay_Payments_Review.xlsx (open)",
                    body=f"Open:\nhttp://{nb_sharepoint_spoof}/open?id=close-payments\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=close-payments"],
                    attachments=[],
                ),
                e(
                    sender_name=nb.line_manager_name,
                    sender_email=mgr_email,
                    subject="Keep an evidence trail for every decision (portal)",
                    body=f"Hi,\n\nFor every decision, log rationale in the portal notes.\n\nThanks,\n{nb.line_manager_name}",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/decision-notes"],
                    attachments=[],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_domain}",
                    subject="Payment recall request received (PDF attached)",
                    body="Hi,\n\nPayment recall request received. Attached request. Follow recall workflow.\n\nPayments",
                    is_phish=False,
                    difficulty=5,
                    category="finance",
                    links=[],
                    attachments=["Payment_Recall_Request.pdf"],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_support_spoof}",
                    subject="RECALL REQUIRED — open attached form now",
                    body="Open attached form immediately to recall.\n\nPayments",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[],
                    attachments=["Recall_Form.pdf.iso"],
                ),
                e(
                    sender_name="CFO Office",
                    sender_email=f"cfo-office@{nb_domain}",
                    subject="Executive update request (portal thread)",
                    body="Hi,\n\nPost an update for execs in the portal thread.\n\nCFO Office",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[f"https://{nb_domain}/finance/close/exec-thread"],
                    attachments=[],
                ),
                e(
                    sender_name="CFO",
                    sender_email=f"cfo@{nb_cfo_spoof}",
                    subject="Exec update: approve via secure link",
                    body=f"Approve via secure link:\nhttp://{nb_cfo_spoof}/approve\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_cfo_spoof}/approve"],
                    attachments=[],
                ),
                e(
                    sender_name="Supplier: Greenlight Maintenance",
                    sender_email="accounts@greenlightmaintenance.co.uk",
                    subject="Invoice INV-77102 (PDF attached)",
                    body="Hi,\n\nInvoice attached.\n\nAccounts",
                    is_phish=False,
                    difficulty=5,
                    category="supplier",
                    links=[],
                    attachments=["INV-77102.pdf"],
                ),
                e(
                    sender_name="Greenlight Maintenance",
                    sender_email="accounts@greenlightmaintenence.co.uk",  # misspelling
                    subject="RE: INV-77102 — view portal message",
                    body="View portal message:\nhttp://greenlightmaintenence.co.uk/portal/msg\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=["http://greenlightmaintenence.co.uk/portal/msg"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Comms",
                    sender_email=f"comms@{nb_domain}",
                    subject="Reminder: phishing reporting during close (PDF attached)",
                    body="Hi,\n\nReminder: report suspicious emails. See attached.\n\nComms",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[],
                    attachments=["Phishing_Reminder_CloseDay.pdf"],
                ),
                e(
                    sender_name="Security Operations",
                    sender_email=f"soc@{nb_domain}",
                    subject="SOC notice: payment redirect campaign observed (portal)",
                    body="Hi,\n\nWe’re seeing payment redirect attempts. See the IOC list in the portal.\n\nSOC",
                    is_phish=False,
                    difficulty=5,
                    category="security",
                    links=[f"https://{nb_domain}/security/ioc/payment-redirect"],
                    attachments=[],
                ),
                e(
                    sender_name="SOC Alerts",
                    sender_email=f"soc-alerts@{nb_support_spoof}",
                    subject="Immediate action: confirm credentials to stop incident",
                    body=f"Confirm credentials:\nhttp://{nb_support_spoof}/incident/confirm\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_support_spoof}/incident/confirm"],
                    attachments=[],
                ),
                e(
                    sender_name="Invoice Processing",
                    sender_email=f"invoices@{nb_domain}",
                    subject="Invoice received: INV-21088 (PDF attached)",
                    body="Hi,\n\nInvoice attached.\n\nInvoice Processing",
                    is_phish=False,
                    difficulty=5,
                    category="finance",
                    links=[],
                    attachments=["INV-21088.pdf"],
                ),
                e(
                    sender_name="Vendor Portal",
                    sender_email=f"no-reply@{nb_doc_spoof}",
                    subject="Close day vendor message — open",
                    body=f"Open message:\nhttp://{nb_doc_spoof}/msg/close-day\n",
                    is_phish=True,
                    difficulty=6,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/msg/close-day"],
                    attachments=[],
                ),
                e(
                    sender_name="Finance Ops",
                    sender_email=f"finance-ops@{nb_domain}",
                    subject="Close pack uploaded (PDF attached)",
                    body="Hi,\n\nClose pack uploaded. Attached summary.\n\nFinance Ops",
                    is_phish=False,
                    difficulty=5,
                    category="internal",
                    links=[],
                    attachments=["ClosePack_Summary.pdf"],
                ),
            ],
            # 3 waves worth (you can trigger only one in frontend for now; or evolve to multiple later)
            wave_emails=[
                # Wave A (e.g., 45s)
                e(
                    sender_name="Accounts Team",
                    sender_email=f"accounts@{nb_domain}",
                    subject="Wave: final approvals needed (portal)",
                    body="Hi,\n\nFinal approvals needed ASAP.\n\nAccounts",
                    is_phish=False,
                    difficulty=6,
                    category="finance",
                    links=[f"https://{nb_domain}/finance/payments/final-approvals"],
                    attachments=[],
                ),
                e(
                    sender_name="CFO",
                    sender_email=f"cfo@{nb_cfo_spoof}",
                    subject="Wave: approve supplier settlement now (secure link)",
                    body=f"Approve now:\nhttp://{nb_cfo_spoof}/settle\n",
                    is_phish=True,
                    difficulty=7,
                    category="phish",
                    links=[f"http://{nb_cfo_spoof}/settle"],
                    attachments=[],
                ),
                e(
                    sender_name="Westridge Supplies",
                    sender_email="billing@westridgesupplies.co.uk",
                    subject="Wave: remittance advice request (PDF attached)",
                    body="Hello,\n\nPlease provide remittance advice once scheduled.\n\nBilling",
                    is_phish=False,
                    difficulty=6,
                    category="supplier",
                    links=[],
                    attachments=["Westridge_Remittance_Request.pdf"],
                ),

                # Wave B (e.g., 90s)
                e(
                    sender_name="IT Security",
                    sender_email=f"security@{nb_domain}",
                    subject="Wave: warning — fake SharePoint links in circulation (PDF attached)",
                    body="Hi,\n\nFake SharePoint links detected. See attached examples.\n\nSecurity",
                    is_phish=False,
                    difficulty=6,
                    category="security",
                    links=[],
                    attachments=["Fake_SharePoint_Examples.pdf"],
                ),
                e(
                    sender_name="Northbridge Utilities SharePoint",
                    sender_email=f"no-reply@{nb_sharepoint_spoof}",
                    subject="Wave: shared file — CloseDay_Exceptions.xlsm",
                    body=f"Open:\nhttp://{nb_sharepoint_spoof}/open?id=exceptions\n",
                    is_phish=True,
                    difficulty=7,
                    category="phish",
                    links=[f"http://{nb_sharepoint_spoof}/open?id=exceptions"],
                    attachments=[],
                ),
                e(
                    sender_name="Payments Desk",
                    sender_email=f"payments@{nb_domain}",
                    subject="Wave: recall workflow reminder (PDF attached)",
                    body="Hi,\n\nReminder: recalls must follow workflow. See attached.\n\nPayments",
                    is_phish=False,
                    difficulty=6,
                    category="finance",
                    links=[],
                    attachments=["Recall_Workflow_Reminder.pdf"],
                ),

                # Wave C (late / “must trigger if user finishes early”)
                e(
                    sender_name="SOC",
                    sender_email=f"soc@{nb_domain}",
                    subject="Wave: IOC list updated (portal)",
                    body="IOC list updated. Review immediately.\n\nSOC",
                    is_phish=False,
                    difficulty=6,
                    category="security",
                    links=[f"https://{nb_domain}/security/ioc/updated"],
                    attachments=[],
                ),
                e(
                    sender_name="SOC Alerts",
                    sender_email=f"soc-alerts@{nb_support_spoof}",
                    subject="Wave: incident containment — verify access",
                    body=f"Verify access:\nhttp://{nb_support_spoof}/containment/verify\n",
                    is_phish=True,
                    difficulty=7,
                    category="phish",
                    links=[f"http://{nb_support_spoof}/containment/verify"],
                    attachments=[],
                ),
                e(
                    sender_name="Internal Audit",
                    sender_email=f"audit@{nb_domain}",
                    subject="Wave: spot check follow-up (PDF attached)",
                    body="Hi,\n\nFollow-up spot check attached.\n\nAudit",
                    is_phish=False,
                    difficulty=6,
                    category="internal",
                    links=[],
                    attachments=["Audit_SpotCheck_FollowUp.pdf"],
                ),
                e(
                    sender_name="Vendor Portal",
                    sender_email=f"no-reply@{nb_doc_spoof}",
                    subject="Wave: vendor message requires signature",
                    body=f"Sign here:\nhttp://{nb_doc_spoof}/sign/close\n",
                    is_phish=True,
                    difficulty=7,
                    category="phish",
                    links=[f"http://{nb_doc_spoof}/sign/close"],
                    attachments=[],
                ),
            ],
        ),
    ]


@transaction.atomic
def seed_curated_levels_and_emails():
    scenario_by_company = {s.company_name: s for s in Scenario.objects.all()}

    defs = []
    defs += _curated_levels_first5(scenario_by_company)
    defs += _curated_levels_6_7(scenario_by_company)
    defs += _curated_levels_8_10(scenario_by_company)

    for ld in defs:
        lvl, _ = Level.objects.update_or_create(
            scenario=ld["scenario"],
            number=ld["number"],
            defaults=dict(title=ld["title"], briefing=ld["briefing"]),
        )

        LevelEmail.objects.filter(level=lvl).delete()

        base = ld.get("emails", ld.get("base_emails", [])) or []
        for idx, em in enumerate(base):
            email, _ = Email.objects.update_or_create(
                mode="simulation",
                scenario=ld["scenario"],
                sender_email=em["sender_email"],
                subject=em["subject"],
                defaults=dict(
                    sender_name=em["sender_name"],
                    body=em["body"],
                    is_phish=em["is_phish"],
                    difficulty=_clamp_difficulty(em.get("difficulty", 1)),
                    category=em.get("category"),
                    links=em.get("links", []) or [],
                    attachments=em.get("attachments", []) or [],
                ),
            )
            email.full_clean()
            email.save()
            LevelEmail.objects.create(level=lvl, email=email, sort_order=idx)

        wave = ld.get("wave_emails", []) or []
        for widx, em in enumerate(wave):
            email, _ = Email.objects.update_or_create(
                mode="simulation",
                scenario=ld["scenario"],
                sender_email=em["sender_email"],
                subject=em["subject"],
                defaults=dict(
                    sender_name=em["sender_name"],
                    body=em["body"],
                    is_phish=em["is_phish"],
                    difficulty=_clamp_difficulty(em.get("difficulty", 1)),
                    category=em.get("category"),
                    links=em.get("links", []) or [],
                    attachments=em.get("attachments", []) or [],
                ),
            )
            email.full_clean()
            email.save()
            LevelEmail.objects.create(level=lvl, email=email, sort_order=100 + widx)

        # Wave emails: 100.. (distinguish without schema change)
        wave = ld.get("wave_emails", []) or []
        for widx, em in enumerate(wave):
            email, _ = Email.objects.update_or_create(
                mode="simulation",
                scenario=ld["scenario"],
                sender_email=em["sender_email"],
                subject=em["subject"],
                defaults=dict(
                    sender_name=em["sender_name"],
                    body=em["body"],
                    is_phish=em["is_phish"],
                    difficulty=em.get("difficulty", 1),
                    category=em.get("category"),
                    links=em.get("links", []) or [],
                    attachments=em.get("attachments", []) or [],
                ),
            )

            email.full_clean()
            email.save()
            LevelEmail.objects.create(level=lvl, email=email, sort_order=100 + widx)

        # Clear existing curated links for this level so re-running seed is stable.
        LevelEmail.objects.filter(level=lvl).delete()

        for idx, e in enumerate(ld["emails"]):
            email, _ = Email.objects.update_or_create(
                mode="simulation",
                scenario=ld["scenario"],
                sender_email=e["sender_email"],
                subject=e["subject"],
                defaults=dict(
                    sender_name=e["sender_name"],
                    body=e["body"],
                    is_phish=e["is_phish"],
                    difficulty=e.get("difficulty", 1),
                    category=e.get("category"),
                    links=e.get("links", []) or [],
                    attachments=e.get("attachments", []) or [],
                ),
            )

            # Enforce your invariants (link XOR attachment + at least one)
            try:
                email.full_clean()
            except Exception as ex:
                print(
                    f"ERROR on email: sender_email={email.sender_email}, subject={email.subject}, error={ex}"
                )
                raise
            email.save()

            LevelEmail.objects.create(level=lvl, email=email, sort_order=idx)


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
            Email.objects.all().delete()
            Scenario.objects.all().delete()
            self.stdout.write(self.style.WARNING("WIPED: all Email + Scenario rows."))

        created_scenarios = 0
        created_sim_emails = 0
        created_arcade_emails = 0

        scenario_seeds = _scenario_seeds()
        for seed in scenario_seeds:
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

            templates = _scenario_email_templates(seed)
            for e in templates:
                email, e_created = Email.objects.update_or_create(
                    scenario=scenario,
                    mode="simulation",
                    sender_email=e["sender_email"],
                    subject=e["subject"],
                    defaults=dict(
                        sender_name=e["sender_name"],
                        body=e["body"],
                        is_phish=e["is_phish"],
                        difficulty=_clamp_difficulty(e.get("difficulty", 1)),
                        category=e.get("category"),
                        links=e.get("links", []) or [],
                        attachments=e.get("attachments", []) or [],
                    ),
                )
                email.full_clean()
                email.save()
                if e_created:
                    created_sim_emails += 1

        seed_curated_levels_and_emails()
        self.stdout.write(self.style.SUCCESS("Seeded curated levels (1–10) with wave emails."))

        Email.objects.filter(mode="arcade").delete()

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
                    difficulty=_clamp_difficulty(e.get("difficulty", 1)),
                    category=e.get("category"),
                    links=e.get("links", []) or [],
                    attachments=e.get("attachments", []) or [],
                ),
            )
            email.full_clean()
            email.save()
            if e_created:
                created_arcade_emails += 1

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(f"- Scenarios: +{created_scenarios} (total {Scenario.objects.count()})")
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
