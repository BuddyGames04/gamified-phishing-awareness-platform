from __future__ import annotations

import random
from typing import Any

from api.models import Scenario


def company_slug(name: str) -> str:
    s = (
        name.lower()
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("'", "")
    )
    parts = [p for p in s.replace("  ", " ").split(" ") if p]
    return "-".join(parts)


def mk_domain(company_name: str) -> str:
    return f"{company_slug(company_name)}.co.uk"


def slug(name: str) -> str:
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


def domain(company_name: str) -> str:
    return f"{slug(company_name)}.co.uk"


def get_scenario(scenario_by_company: dict[str, Scenario], name: str) -> Scenario:
    try:
        return scenario_by_company[name]
    except KeyError:
        raise KeyError(f"Missing Scenario for company_name={name!r}")


def clamp_difficulty(d: int) -> int:
    return max(1, min(5, int(d)))


def maybe(prob: float) -> bool:
    return random.random() < prob


def ensure_xor_links_attachments(e: dict[str, Any]) -> dict[str, Any]:
    links = e.get("links") or []
    atts = e.get("attachments") or []
    if (len(links) > 0) == (len(atts) > 0):
        raise ValueError(
            f"Email violates XOR invariant: subject={e.get('subject')} links={links} attachments={atts}"
        )
    return e


def bad_url_variants(url: str) -> str:
    variants = [
        url.replace("https://", "http//"),
        url.replace("https://", "hxxp://"),
        url.replace("https://", "http://").replace(".", " ."),
        url.replace("https://", ""),
        url.replace("https://", "http://").replace(".co.uk", ".con"),
        url.replace("https://", "http://").replace("/", " / "),
    ]
    return random.choice(variants)


def userinfo_trick(real_domain: str, evil_domain: str, path: str) -> str:
    return f"https://{real_domain}@{evil_domain}/{path.lstrip('/')}"


def lookalike_domain(domain_name: str, difficulty: int) -> str:
    base = domain_name.replace(".co.uk", "").replace(".com", "").replace(".ac.uk", "")
    tld = ".co.uk" if domain_name.endswith(".co.uk") else ".com"
    if difficulty <= 2:
        return f"{base}-verify{tld}"
    if difficulty == 3:
        return f"{base}-security{tld}"
    if difficulty == 4:
        return f"secure.{base}{tld}.login"
    return f"{base}-portal{tld}"


def attachment_for(diff: int, is_phish: bool) -> str:
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
        return random.choice(safe_pdfs + safe_office)

    if diff == 1:
        return random.choice(
            ["FREE_GIFT_CARD.exe", "invoiceeeee.pdf.exe", "voicemail.htm", "open_me_now.scr"]
        )
    if diff == 2:
        return random.choice(risky)
    if diff == 3:
        return random.choice(risky + ["Invoice_2026-02.pdf.iso", "PaymentAdvice.docm"])
    if diff == 4:
        return random.choice(["Invoice.pdf.iso", "RemittanceAdvice.docm", "Statement.pdf.exe"])
    return random.choice(safe_pdfs)

def slugify_company(name: str) -> str:
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


def domain_for_company(company_name: str) -> str:
    return f"{slugify_company(company_name)}.co.uk"