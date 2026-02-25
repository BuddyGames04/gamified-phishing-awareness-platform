from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from api.management.seeders.common import (
    attachment_for,
    bad_url_variants,
    clamp_difficulty,
    ensure_xor_links_attachments,
    lookalike_domain,
    maybe,
    slug,
    userinfo_trick,
)
from api.models import Email


def arcade_emails() -> List[Dict[str, Any]]:
    emails: List[Dict[str, Any]] = []

    BANKS = ["NatWest", "Barclays", "Lloyds", "HSBC", "Santander"]
    DELIVERY = ["Royal Mail", "DPD", "Evri", "DHL", "UPS"]
    CLOUD = ["Dropbox", "OneDrive", "Google Drive", "WeTransfer", "DocuSign"]
    MARKET = ["Amazon", "eBay", "PayPal", "Vinted"]
    ORGS = ["FitClub", "CityGym", "SwimCentre", "CinemaPass", "LibraryPlus"]
    UNIS = ["Kestrel University", "Northbridge University", "Southwick University"]

    LEGIT_PORTAL = {
        "bank": "secure-notifications.co.uk",
        "delivery": "parcel-service.co.uk",
        "cloud": "portal-services.co.uk",
        "membership": "memberships.co.uk",
        "uni": "university.ac.uk",
        "market": "account-portal.co.uk",
    }

    def url_in_body(diff: int) -> bool:
        diff = clamp_difficulty(diff)
        if diff <= 2:
            return True
        if diff == 5:
            return maybe(0.03)
        if diff == 4:
            return maybe(0.08)
        return maybe(0.15)

    def format_body(diff: int, body: str, url: Optional[str]) -> str:
        if not url:
            return body
        if not url_in_body(diff):
            return body + "\n\nOpen the link using the button above in the email client.\n"
        return body + f"\n\nLink:\n{url}\n"

    def make_legit(diff: int) -> Dict[str, Any]:
        diff = clamp_difficulty(diff)
        kind = random.choice(["delivery", "cloud", "membership", "uni", "invoice"])
        ref = random.randint(100000, 999999)

        if kind == "delivery":
            brand = random.choice(DELIVERY)
            dom = LEGIT_PORTAL["delivery"]
            url = f"https://{dom}/track/{ref}"
            body = f"Hi,\n\nYour parcel tracking has been updated.\nTracking number: {ref}\n\nThanks,\n{brand} Notifications"
            if maybe(0.35):
                e = dict(
                    sender_name=f"{brand} Notifications",
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: Tracking update ({ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="delivery",
                    links=[],
                    attachments=[f"Delivery_Notice_{ref}.pdf"],
                )
            else:
                e = dict(
                    sender_name=f"{brand} Notifications",
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: Tracking update ({ref})",
                    body=format_body(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="delivery",
                    links=[url],
                    attachments=[],
                )
            return ensure_xor_links_attachments(e)

        if kind == "cloud":
            brand = random.choice(CLOUD)
            dom = LEGIT_PORTAL["cloud"]
            doc = random.choice(
                ["Policy_Update.pdf", "Meeting_Notes.pdf", "Project_Brief.pdf", "Budget_Summary.pdf"]
            )
            url = f"https://{dom}/files/view/{slug(doc)}?ref={ref}"
            body = f"A file has been shared with you.\n\nFile: {doc}\n\nThanks,\n{brand}"
            if maybe(0.25):
                e = dict(
                    sender_name=brand,
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: File shared with you (Ref {ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="cloud",
                    links=[],
                    attachments=[f"Share_Receipt_{ref}.pdf"],
                )
            else:
                e = dict(
                    sender_name=brand,
                    sender_email=f"no-reply@{dom}",
                    subject=f"{brand}: File shared with you (Ref {ref})",
                    body=format_body(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="cloud",
                    links=[url],
                    attachments=[],
                )
            return ensure_xor_links_attachments(e)

        if kind == "membership":
            org = random.choice(ORGS)
            dom = LEGIT_PORTAL["membership"]
            url = f"https://{dom}/{slug(org)}/account"
            body = f"Hi,\n\nYour {org} membership is active.\n\nThanks,\n{org}"
            if maybe(0.30):
                e = dict(
                    sender_name=org,
                    sender_email=f"noreply@{dom}",
                    subject=f"Welcome to {org} — membership active (Ref {ref})",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="subscription",
                    links=[],
                    attachments=[f"{org}_Welcome_{ref}.pdf"],
                )
            else:
                e = dict(
                    sender_name=org,
                    sender_email=f"noreply@{dom}",
                    subject=f"Welcome to {org} — membership active (Ref {ref})",
                    body=format_body(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="subscription",
                    links=[url],
                    attachments=[],
                )
            return ensure_xor_links_attachments(e)

        if kind == "uni":
            uni = random.choice(UNIS)
            dom = LEGIT_PORTAL["uni"]
            url = f"https://{dom}/portal/timetable?week={random.randint(1, 12)}"
            body = "Hi,\n\nYour timetable has been updated. Please check the student portal.\n\nRegistry"
            if maybe(0.30):
                e = dict(
                    sender_name=f"{uni} Registry",
                    sender_email=f"registry@{dom}",
                    subject="Timetable update available",
                    body=body,
                    is_phish=False,
                    difficulty=diff,
                    category="education",
                    links=[],
                    attachments=[f"Timetable_Summary_{ref}.pdf"],
                )
            else:
                e = dict(
                    sender_name=f"{uni} Registry",
                    sender_email=f"registry@{dom}",
                    subject="Timetable update available",
                    body=format_body(diff, body, url),
                    is_phish=False,
                    difficulty=diff,
                    category="education",
                    links=[url],
                    attachments=[],
                )
            return ensure_xor_links_attachments(e)

        vendor = random.choice(
            ["BrightCables Ltd", "Westridge Supplies", "Greenlight Maintenance", "OfficeMart"]
        )
        dom = f"{slug(vendor).replace('-ltd','')}.co.uk"
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
        return ensure_xor_links_attachments(e)

    def make_phish(diff: int) -> Dict[str, Any]:
        diff = clamp_difficulty(diff)
        kind = random.choice(["bank", "delivery", "cloud", "account", "invoice"])
        ref = random.randint(100000, 999999)

        evil_root = random.choice(
            [
                "account-security-alerts.com",
                "secure-authentication.co",
                "portal-verification.com",
                "service-login.co",
                "customer-support-portal.com",
            ]
        )

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

        if kind == "bank":
            bank = random.choice(BANKS)
            legit_dom = LEGIT_PORTAL["bank"]
            look = lookalike_domain(legit_dom, diff)
            subject = f"{bank}: unusual login attempt detected (Case {ref})"
            if diff <= 2:
                subject = f"URGENT: {bank} Unusual Login attempt Detected"
            if diff == 5:
                url = userinfo_trick(legit_dom, evil_root, f"verify/session/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/secure/{bank.lower()}/review/{ref}"
            elif diff == 3:
                url = f"https://{look}/login/review/{ref}"
            elif diff == 2:
                url = f"http://{look}/verify"
            else:
                url = bad_url_variants(f"https://{look}/verify-now")
            body = (
                "Dear customer,\n\n"
                "We detected a sign-in attempt that may not have been you.\n"
                f"If you did not request this, secure your account {urgency}.\n"
            )
            e = dict(
                sender_name=f"{bank} Security",
                sender_email=f"security@{look}",
                subject=subject,
                body=format_body(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="banking",
                links=[url],
                attachments=[],
            )
            return ensure_xor_links_attachments(e)

        if kind == "delivery":
            carrier = random.choice(DELIVERY)
            legit_dom = LEGIT_PORTAL["delivery"]
            look = lookalike_domain(legit_dom, diff)
            subject = f"{carrier}: delivery issue — action required"
            if diff == 5:
                url = userinfo_trick(legit_dom, evil_root, f"reschedule/{ref}")
            elif diff == 4:
                url = f"https://delivery.{legit_dom}.{evil_root}/slot/{ref}"
            elif diff == 3:
                url = f"https://{look}/reschedule/{ref}"
            elif diff == 2:
                url = f"http://{look}/confirm-slot"
            else:
                url = bad_url_variants(f"https://{look}/reschedule")
            body = (
                "We attempted delivery but couldn't complete it.\n"
                f"Please confirm a new delivery slot {urgency} to avoid return.\n"
            )
            e = dict(
                sender_name=f"{carrier} Notifications",
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=format_body(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="delivery",
                links=[url],
                attachments=[],
            )
            return ensure_xor_links_attachments(e)

        if kind == "cloud":
            brand = random.choice(CLOUD)
            legit_dom = LEGIT_PORTAL["cloud"]
            look = lookalike_domain(legit_dom, diff)
            doc = random.choice(
                ["Shared_Document.pdf", "Policy_Update.pdf", "AccessReview_Q1.xlsx", "Invoice_Copy.pdf"]
            )
            subject = f"{brand}: shared document"
            if diff <= 2:
                subject = f"{brand} - Shared file requires login"
            if diff == 5:
                url = userinfo_trick(legit_dom, evil_root, f"doc/open/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/s/{ref}/open"
            elif diff == 3:
                url = f"https://{look}/doc/open?id={ref}"
            elif diff == 2:
                url = f"http://{look}/open?id={ref}"
            else:
                url = bad_url_variants(f"https://{look}/open?id={ref}")
            body = f"A document has been shared with you.\nFile: {doc}\nSign in to view.\n"
            e = dict(
                sender_name=brand,
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=format_body(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="cloud",
                links=[url],
                attachments=[],
            )
            return ensure_xor_links_attachments(e)

        if kind == "account":
            brand = random.choice(MARKET + CLOUD)
            legit_dom = LEGIT_PORTAL["market"]
            look = lookalike_domain(legit_dom, diff)
            subject = f"{brand}: account security notice (Ref {ref})"
            if diff <= 2:
                subject = f"{brand} ACCOUNT LOCKED - VERIFY NOW"
            if diff == 5:
                url = userinfo_trick(legit_dom, evil_root, f"restore/{brand.lower()}/{ref}")
            elif diff == 4:
                url = f"https://{evil_root}/account/restore/{ref}"
            elif diff == 3:
                url = f"https://{look}/restore/{ref}"
            elif diff == 2:
                url = f"http://{look}/verify"
            else:
                url = bad_url_variants(f"https://{look}/verify")
            body = (
                "We detected activity that requires verification.\n"
                f"To avoid restricted access, confirm your details {urgency}.\n"
            )
            e = dict(
                sender_name=f"{brand} Support",
                sender_email=f"no-reply@{look}",
                subject=subject,
                body=format_body(diff, body, url),
                is_phish=True,
                difficulty=diff,
                category="account",
                links=[url],
                attachments=[],
            )
            return ensure_xor_links_attachments(e)

        vendor = random.choice(["BrightCables", "OfficeMart", "Greenlight", "Westridge"])
        inv = f"INV-{random.randint(10000, 99999)}"
        sender_dom = f"{slug(vendor)}.co.uk" if diff >= 4 else f"{slug(vendor)}-billing.co"
        subject = f"Invoice attached: {inv}"
        if diff <= 2:
            subject = f"OVERDUE {inv}!!! OPEN ATTACHMENT"
        body = f"Hello,\n\nPlease see attached invoice {inv}.\nLet us know once scheduled.\n\nThanks,\nAccounts"
        att = attachment_for(diff, is_phish=True)
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
        return ensure_xor_links_attachments(e)

    for diff in range(1, 6):
        for _ in range(10):
            emails.append(make_legit(diff))
        for _ in range(10):
            emails.append(make_phish(diff))

    for _ in range(10):
        real_dom = LEGIT_PORTAL["bank"]
        evil_dom = random.choice(["login-review.co", "secure-casework.com", "identity-checks.co"])
        ref = random.randint(100000, 999999)

        if maybe(0.5):
            url = userinfo_trick(real_dom, evil_dom, f"case/{ref}/review")
            body = (
                "Hi,\n\nFollowing up on the security review opened for your account.\n"
                "Please confirm you recognise the sign-in record.\n\nThanks,\nSecurity Operations"
            )
            emails.append(
                ensure_xor_links_attachments(
                    dict(
                        sender_name="Security Operations",
                        sender_email=f"soc@{real_dom}",
                        subject="Security review follow-up",
                        body=format_body(5, body, url),
                        is_phish=True,
                        difficulty=5,
                        category="security",
                        links=[url],
                        attachments=[],
                    )
                )
            )
        else:
            att = attachment_for(5, is_phish=True)
            body = (
                "Hi,\n\nAttached is the confirmation document requested for today.\n"
                "If anything is incorrect, reply and we’ll amend it.\n\nThanks,\nAccounts"
            )
            emails.append(
                ensure_xor_links_attachments(
                    dict(
                        sender_name="Accounts Team",
                        sender_email=f"accounts@{real_dom}",
                        subject="Confirmation document attached",
                        body=body,
                        is_phish=True,
                        difficulty=5,
                        category="spearphish",
                        links=[],
                        attachments=[att],
                    )
                )
            )

    random.shuffle(emails)
    return emails


def seed_arcade_emails() -> int:
    Email.objects.filter(mode="arcade").delete()
    created = 0
    for e in arcade_emails():
        email, e_created = Email.objects.update_or_create(
            scenario=None,
            mode="arcade",
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
            created += 1
    return created