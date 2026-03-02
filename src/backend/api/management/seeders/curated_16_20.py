# src/backend/api/management/seeders/curated_16_20.py
from __future__ import annotations

from typing import Any

from api.management.seeders.common import domain_for_company, slugify_company


def curated_levels_16_20(scenario_by_company) -> list[dict[str, Any]]:
    """
    Levels 16–20: endgame realism under breach conditions.
    - Company has suffered a data breach
    - Sophos email protection degraded (higher phish volume)
    - Highly targeted spear phish: 1–2 max per level
    - 22–28 base emails
    - 3 wave injections
    - Threads overlap across IT/Sec/Legal/Finance/HR/Facilities/External vendors
    """

    def get(company_name: str):
        try:
            return scenario_by_company[company_name]
        except KeyError as e:
            raise KeyError(f"Missing Scenario for company_name={company_name!r}") from e

    nb = get("Northbridge Utilities")
    hl = get("Harbourline Logistics")
    rs = get("Redwood Software")
    ku = get("Kestrel University")

    mapping = {
        16: nb,
        17: rs,
        18: hl,
        19: ku,
        20: nb,
    }

    level_overrides = {
        16: {
            "role_title": "Operations Finance Lead (Acting) — Breach Response",
            "department_name": "Operations Finance, Supplier Controls & Incident Support",
            "responsibilities": [
                "Maintain payment controls during incident disruption; no policy bypasses.",
                "Coordinate bank-detail change verification and evidence capture for audit.",
                "Support incident comms: route vendor and staff queries via approved portals.",
                "Keep delivery/access constraints moving without leaking personal data.",
                "Document decisions and rationale (audit trail) under high email volume.",
                "Team (direct reports):",
                "- Mia Patel (Finance Assistant — invoices & matching)",
                "- Jordan Reeves (Controls Analyst — approvals & audit trail)",
                "- Sana Ahmed (Ops Coordinator — supplier comms & delivery slots)",
            ],
            "intro_text": (
                "Northbridge has confirmed a data breach and Sophos email protection is degraded. "
                "Expect higher phishing volume, including highly targeted spear phishing that matches ongoing "
                "threads (bank changes, incident comms, audit evidence). You must keep operations moving without "
                "breaking verification policy. Use portals directly and record evidence."
            ),
        },
        17: {
            "role_title": "Engineering Operations Manager — Incident Coordination",
            "department_name": "Engineering Ops, Security Enablement & Vendor Governance",
            "responsibilities": [
                "Coordinate release readiness under incident constraints and tooling instability.",
                "Route security comms via incident portal; avoid credential workflows from email links.",
                "Manage vendor renewals/legal docs; ensure evidence trail and approvals are captured.",
                "Coordinate access reviews and emergency credential resets via official IT portal only.",
                "Support managers with admin requests while maintaining incident discipline.",
                "Team (matrix):",
                "- Priya Nair (Release Coordinator)",
                "- Theo Grant (IT Liaison)",
                "- Elena Volkova (Procurement & Renewals)",
            ],
            "intro_text": (
                "Redwood is responding to a breach while continuing critical deliveries/releases. "
                "Sophos filtering is degraded and attackers are exploiting incident comms. "
                "You’ll see legitimate incident updates and polished spear phish that mimic them."
            ),
        },
        18: {
            "role_title": "Depot Operations Manager — Breach & Continuity",
            "department_name": "Depot Ops, Fleet, People & Continuity",
            "responsibilities": [
                "Maintain depot continuity during incident week and staffing pressure.",
                "Approve sickness/cover while minimising personal data exposure in email.",
                "Handle carrier and customs comms; verify changes via portals only.",
                "Coordinate finance controls: no bank change approvals via email.",
                "Escalate suspicious customs/courier comms; preserve evidence for investigations.",
                "Team (shift leads):",
                "- Callum Price (AM Shift Lead)",
                "- Aisha Khan (PM Shift Lead)",
                "- Rory Sinclair (Fleet Coordinator)",
            ],
            "intro_text": (
                "Harbourline is operating under pressure: customs delays, staffing gaps, and incident-related "
                "process changes. Sophos filtering is degraded; attackers are using real shipment and slot "
                "references to spear phish. Keep the depot moving without breaking verification steps."
            ),
        },
        19: {
            "role_title": "School Operations & Compliance Liaison",
            "department_name": "School Ops, HR Liaison, Finance Support & Incident Comms",
            "responsibilities": [
                "Coordinate events/timetabling/facilities under incident comms restrictions.",
                "Route HR/pay queries via portal; minimise PII exposure in email threads.",
                "Support finance compliance and supplier paperwork with strict verification.",
                "Track multiple overlapping threads; avoid reacting to urgency without confirmation.",
                "Ensure staff follow incident guidance during Sophos degradation window.",
            ],
            "intro_text": (
                "Kestrel is in event week while responding to a breach and degraded email filtering. "
                "Phish will look like familiar university portals and internal notices. "
                "Maintain discipline: use portals directly and confirm requests via approved channels."
            ),
        },
        20: {
            "role_title": "Ops Finance Lead (Acting) — Incident Command Support",
            "department_name": "Operations Finance & Incident Command (Supplier Controls)",
            "responsibilities": [
                "Run payment approvals and exceptions under incident command constraints.",
                "Coordinate with Legal/Audit on evidence capture and disclosure timelines.",
                "Maintain supplier bank-change verification; no exceptions, even under pressure.",
                "Support staff queries and facilities constraints while maintaining PII discipline.",
                "Detect and report spear phishing exploiting live incident threads.",
                "Team (direct reports):",
                "- Mia Patel (Finance Assistant — invoices & matching)",
                "- Jordan Reeves (Controls Analyst — approvals & audit trail)",
                "- Sana Ahmed (Ops Coordinator — supplier comms & delivery slots)",
            ],
            "intro_text": (
                "Final level: full operational overload. Breach fallout, audit evidence requests, supplier pressure, "
                "banking verification and IT instability overlap. Sophos filtering is degraded, and attackers are "
                "highly targeted. Expect 1–2 spear phish that closely match your active threads."
            ),
        },
    }

    def clean_mgr_name(name: str) -> str:
        return (
            name.replace(".", "")
            .replace(",", "")
            .lower()
            .replace("  ", " ")
            .strip()
            .replace(" ", ".")
        )

    def e(**kwargs):
        links = list(kwargs.get("links") or [])
        attachments = list(kwargs.get("attachments") or [])

        # XOR policy (matches your existing helper):
        # if both present, keep attachments and clear links
        if links and attachments:
            links = []
            kwargs["links"] = []
            kwargs["attachments"] = attachments

        # if neither present, generate a default internal thread link
        if not links and not attachments:
            dom = kwargs.get("dom", "internal")
            slug = kwargs.get("slug", "thread")
            kwargs["links"] = [f"https://{dom}/portal/inbox/thread?subject={slug}"]
            kwargs["attachments"] = []

        kwargs["links"] = kwargs.get("links") or links
        kwargs["attachments"] = kwargs.get("attachments") or attachments

        return dict(**kwargs)

    defs: list[dict[str, Any]] = []

    for level_no, scenario in mapping.items():
        dom = domain_for_company(scenario.company_name)
        slug = slugify_company(scenario.company_name)
        mgr_email = f"{clean_mgr_name(scenario.line_manager_name)}@{dom}"

        # Spoof domains
        # Keep these *less cartoonish* than early levels; still separate from internal domain.
        sharepoint_spoof = f"{slug}-sharepoint.com"
        helpdesk_spoof = f"{slug}-helpdesk.com"
        docs_spoof = f"{slug}-docs.com"
        finance_spoof = f"{slug}-finance.com"
        payroll_spoof = f"{slug}-payroll.com"
        hr_spoof = f"{slug}-hr.com"
        vendorhub_spoof = f"{slug}-vendorhub.com"
        bank_spoof = f"{slug}-banking.com"
        incident_spoof = f"{slug}-incident.com"  # spear-friendly look

        finance_portal = f"https://{dom}/finance"
        hr_portal = f"https://{dom}/hr"
        it_portal = f"https://{dom}/it"
        facilities_portal = f"https://{dom}/facilities"
        vendor_portal = f"https://{dom}/procurement/vendors"
        docs_portal = f"https://{dom}/portal/docs"
        incident_portal = f"https://{dom}/security/incident"

        # -------------------------
        # LEVEL 16 (NB)
        # -------------------------
        if level_no == 16:
            defs.append(
                dict(
                    scenario=scenario,
                    number=16,
                    title="Breach week: controls under pressure (Sophos degraded)",
                    briefing=(
                        "Breach confirmed. Email filtering degraded. Keep payment controls and evidence capture "
                        "intact while staff and vendors push for quick action. Expect 1 spear phish that matches "
                        "a real incident thread."
                    ),
                    scenario_overrides=level_overrides.get(16, {}),
                    base_emails=[
                        e(
                            sender_name="CISO Office",
                            sender_email=f"ciso-office@{dom}",
                            subject="Incident update: breach confirmed — follow approved comms only (portal)",
                            body=(
                                "Breach confirmed. Do not share incident details by email.\n"
                                "Use the incident portal for updates, Q&A, and evidence submission.\n"
                                "Sophos email filtering is degraded; assume increased phishing."
                            ),
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"{incident_portal}/updates?ref=INC-2026-04"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Notice: Sophos email protection degraded — increased phishing expected (status)",
                            body="Filtering degraded. Do not trust email links for auth/credentials. Use portals directly.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/sophos-degraded"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Internal Audit",
                            sender_email=f"audit@{dom}",
                            subject="Audit instruction: preserve evidence of bank-change approvals (portal upload)",
                            body="Upload screenshots/notes for any bank-change approvals this week. Deadline EOD.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"{finance_portal}/audit/evidence/upload?topic=bank-changes&week=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Finance Controls",
                            sender_email=f"controls@{dom}",
                            subject="Incident week: NO bank-change approvals from email (policy reminder)",
                            body="Reminder: verify changes via vendor portal + out-of-band confirmation. No exceptions.",
                            is_phish=False,
                            difficulty=5,
                            category="finance",
                            links=[f"{finance_portal}/controls/bank-changes/policy"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Procurement System",
                            sender_email=f"no-reply@{dom}",
                            subject="Vendor bank change request: BC-9133 (verification required)",
                            body="Verification steps required before approval.",
                            is_phish=False,
                            difficulty=5,
                            category="procurement",
                            links=[f"{vendor_portal}/bank-changes/verify?case=BC-9133"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Westridge Supplies",
                            sender_email="billing@westridgesupplies.co.uk",
                            subject="RE: BC-9133 verification — can you confirm call-back window?",
                            body=(
                                "Hello,\n\nWe raised the bank change in the portal. "
                                "Can you confirm a call-back window today for verification?\n\nBilling"
                            ),
                            is_phish=False,
                            difficulty=5,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Payroll Team",
                            sender_email=f"payroll@{dom}",
                            subject="Incident week: payroll exception list — managers review required (portal)",
                            body="Please review exception list by 16:00. Do not send payslips via email.",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[f"{hr_portal}/payroll/exceptions?run=monthly&context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Staff guidance: minimise PII in email during incident",
                            body="Use HR portal for absence/pay cases. Avoid emailing personal details.",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[f"{hr_portal}/policy/pii-minimisation?incident=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Delivery today: replacement chairs — confirm loading bay slot",
                            body="Confirm loading bay slot and escort contact in portal.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/deliveries/confirm?ref=CHAIR-1902"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Site Security",
                            sender_email=f"security@{dom}",
                            subject="Visitor list request: CHAIR-1902 delivery (portal upload)",
                            body="Upload visitor list via facilities portal. Do not email names externally.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"{facilities_portal}/visitors/upload?ref=CHAIR-1902"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Invoice Processing",
                            sender_email=f"invoices@{dom}",
                            subject="Invoice received: INV-25112 (PDF attached)",
                            body="Invoice attached. Please process per policy and record exceptions.",
                            is_phish=False,
                            difficulty=5,
                            category="finance",
                            links=[],
                            attachments=["INV-25112.pdf"],
                        ),
                        e(
                            sender_name="Service Desk",
                            sender_email=f"support@{dom}",
                            subject="Ticket: finance portal permissions — updated notes (portal)",
                            body="Your ticket has updated notes; review and proceed as instructed.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/servicedesk/tickets/SD-26211"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Security Operations",
                            sender_email=f"soc@{dom}",
                            subject="Reminder: attackers spoof internal comms during incidents",
                            body="If email asks for credential login or urgent approval, navigate to portal directly.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"{incident_portal}/guidance/phishing"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Jordan Reeves",
                            sender_email=f"jordan.reeves@{dom}",
                            subject="Bank change BC-9133 — I’ve started evidence pack (where should I upload?)",
                            body="I’ve got screenshots and call notes ready. Which portal upload should I use?",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Keep an audit trail — don’t shortcut verification even if it’s loud",
                            body="If anyone pressures you to approve via email, refuse and route via portal + call-back.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/portal/notes/ops-finance?week=incident"],
                            attachments=[],
                        ),
                        # ---- spear phish (1 max for level 16) ----
                        e(
                            sender_name="Incident Response Portal",
                            sender_email=f"no-reply@{incident_spoof}",
                            subject="INC-2026-04: evidence upload required for BC-9133 (deadline today)",
                            body=(
                                "Incident evidence request linked to bank-change case BC-9133.\n"
                                "Upload your evidence pack here:\n"
                                f"http://{incident_spoof}/evidence/upload?case=BC-9133&ref=INC-2026-04\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{incident_spoof}/evidence/upload?case=BC-9133&ref=INC-2026-04"],
                            attachments=[],
                        ),
                        # additional realistic noise
                        e(
                            sender_name="Comms Team",
                            sender_email=f"comms@{dom}",
                            subject="Holding statement draft — internal only (portal)",
                            body="Draft posted in comms portal. Do not forward externally.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/comms/incident/holding-statement?ref=INC-2026-04"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Vendor: SecureSure Cyber Insurance",
                            sender_email="claims@securesure-insurance.co.uk",
                            subject="Incident notification acknowledgment — claim reference ISS-44190",
                            body="Acknowledged. Next steps will be sent via your nominated incident contact.",
                            is_phish=False,
                            difficulty=5,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Procurement Portal",
                            sender_email=f"no-reply@{dom}",
                            subject="Vendor profile update: contact details amended (portal)",
                            body="Review vendor contact changes (non-financial) in portal.",
                            is_phish=False,
                            difficulty=5,
                            category="procurement",
                            links=[f"{vendor_portal}/changes/pending?case=VND-6021"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Sana Ahmed",
                            sender_email=f"sana.ahmed@{dom}",
                            subject="Delivery escort: who should I list as escort for CHAIR-1902?",
                            body="Portal asks for an escort name + mobile. Who should I put?",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Wave: Sophos degradation continuing — report suspicious emails via portal",
                            body="Use the security report portal; do not forward suspicious emails to colleagues.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/sophos-degraded?update=2"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Wave: CHAIR-1902 delivery moved earlier — confirm escort ASAP",
                            body="Driver can arrive 30 mins earlier. Confirm escort now.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/deliveries/confirm?ref=CHAIR-1902&update=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="VendorHub Notifications",
                            sender_email=f"no-reply@{vendorhub_spoof}",
                            subject="Wave: BC-9133 pending — confirm to prevent payment failure",
                            body=f"Confirm:\nhttp://{vendorhub_spoof}/confirm?case=BC-9133\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{vendorhub_spoof}/confirm?case=BC-9133"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # -------------------------
        # LEVEL 17 (RS)
        # -------------------------
        if level_no == 17:
            defs.append(
                dict(
                    scenario=scenario,
                    number=17,
                    title="Incident coordination: renewals + access governance + spear phishing",
                    briefing=(
                        "Release and vendor governance continues during an incident. Sophos filtering degraded. "
                        "Expect high-quality impersonation of incident updates and vendor/legal workflows (1 spear)."
                    ),
                    scenario_overrides=level_overrides.get(17, {}),
                    base_emails=[
                        e(
                            sender_name="Security Operations",
                            sender_email=f"soc@{dom}",
                            subject="Incident notice: do not use emailed links for auth resets (portal)",
                            body="Navigate to IT portal directly for password/MFA resets. Attackers are spoofing notices.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/incident/INC-2026-07/guidance"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Status: Sophos email protection degraded (phishing risk)",
                            body="Expect higher phishing volume; treat unexpected workflow emails as suspicious.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/sophos-degraded"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Release Coordination",
                            sender_email=f"release@{dom}",
                            subject="Release readiness: sign-off required despite incident (portal)",
                            body="Checklist ready. Please sign off once DPA status is confirmed.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/engineering/release/readiness?rel=R-24.4&context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Legal Ops",
                            sender_email=f"legal@{dom}",
                            subject="DPA addendum ready — assign approver (portal)",
                            body="Addendum posted. Use legal portal; do not sign from emailed links.",
                            is_phish=False,
                            difficulty=5,
                            category="legal",
                            links=[f"https://{dom}/legal/dpa/DPA-3510?context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Procurement & Renewals",
                            sender_email=f"renewals@{dom}",
                            subject="Renewal due: CloudLogs — quote attached",
                            body="Quote attached. Confirm cost centre and approver.",
                            is_phish=False,
                            difficulty=5,
                            category="procurement",
                            links=[],
                            attachments=["CloudLogs_Renewal_Quote.pdf"],
                        ),
                        e(
                            sender_name="Security Governance",
                            sender_email=f"security@{dom}",
                            subject="Access review: incident exception list (portal)",
                            body="Complete incident exception access review and record rationale.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/access-reviews/AR-7902?incident=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Theo Grant",
                            sender_email=f"theo.grant@{dom}",
                            subject="Heads up: multiple fake 'incident portal' emails going around",
                            body="SOC says to ignore emailed logins. Can you reinforce that in your replies?",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Service Desk",
                            sender_email=f"support@{dom}",
                            subject="Ticket: emergency credential reset requests — triage notes (portal)",
                            body="High volume. Follow portal flow only. Update triage status.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/servicedesk/tickets/SD-27190"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Vendor: CloudLogs",
                            sender_email="renewals@cloudlogs.io",
                            subject="RE: renewal — can you confirm who signs DPAs during incident?",
                            body="We need a named approver and expected date for the DPA addendum.",
                            is_phish=False,
                            difficulty=5,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Internal Comms",
                            sender_email=f"comms@{dom}",
                            subject="Draft: staff incident FAQ — review before posting (portal)",
                            body="FAQ posted for review. Keep language consistent; no extra details by email.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/comms/incident/faq/draft?ref=INC-2026-07"],
                            attachments=[],
                        ),
                        e(
                            sender_name="CI System",
                            sender_email=f"ci@{dom}",
                            subject="Build pipeline report (PDF attached) — check before sign-off",
                            body="Report attached. Confirm no regression before release sign-off.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[],
                            attachments=["Pipeline_Performance_Report_R-24.4.pdf"],
                        ),
                        e(
                            sender_name="Elena Volkova",
                            sender_email=f"elena.volkova@{dom}",
                            subject="Renewal routing: which cost centre for CloudLogs?",
                            body="Need cost centre + approver name for PO routing.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        # spear phish (1 max for level 17) — mimics incident update + access review
                        e(
                            sender_name="Security Incident Updates",
                            sender_email=f"no-reply@{incident_spoof}",
                            subject="INC-2026-07: access review submission requires re-authentication",
                            body=(
                                "To submit the incident exception access review, re-authenticate now:\n"
                                f"http://{incident_spoof}/auth/review?ar=AR-7902&ref=INC-2026-07\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{incident_spoof}/auth/review?ar=AR-7902&ref=INC-2026-07"],
                            attachments=[],
                        ),
                        # additional realistic phish noise (non-spear)
                        e(
                            sender_name="IT Admin",
                            sender_email=f"admin@{helpdesk_spoof}",
                            subject="MFA enforcement: verify device to avoid lockout",
                            body=f"Verify:\nhttp://{helpdesk_spoof}/mfa/verify\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/mfa/verify"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Shared Drive",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared: Incident_FAQ_Final.docx (open)",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=incident-faq-final\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{sharepoint_spoof}/open?id=incident-faq-final"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Legal Ops",
                            sender_email=f"legal@{dom}",
                            subject="Reminder: do not sign vendor docs from emailed links (policy)",
                            body="Use internal legal portal for signing workflows.",
                            is_phish=False,
                            difficulty=5,
                            category="legal",
                            links=[f"https://{dom}/legal/policy/signing?context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Travel Desk",
                            sender_email=f"travel@{dom}",
                            subject="Travel itinerary ready — confirm if still needed due to incident (portal)",
                            body="Itinerary posted. Confirm proceed/hold.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/travel/itineraries/T-5901?context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Vendor: IssueTracker Pro",
                            sender_email="billing@issuetrackerpro.com",
                            subject="Renewal follow-up — can you confirm PO timeline?",
                            body="We can hold pricing for 7 days. Please confirm expected PO date.",
                            is_phish=False,
                            difficulty=5,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="IssueTracker Billing",
                            sender_email=f"billing@{vendorhub_spoof}",
                            subject="Payment method update required to prevent interruption",
                            body=f"Update:\nhttp://{vendorhub_spoof}/billing/update\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{vendorhub_spoof}/billing/update"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Release Coordination",
                            sender_email=f"release@{dom}",
                            subject="Wave: release sign-off window shortened (incident constraints)",
                            body="Please prioritise sign-off once DPA status is confirmed.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/engineering/release/readiness?rel=R-24.4&urgent=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Security Governance",
                            sender_email=f"security@{dom}",
                            subject="Wave: access review closes today — managers must submit rationale",
                            body="Submit via portal only; include rationale for any exceptions.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/access-reviews/AR-7902?due=today"],
                            attachments=[],
                        ),
                        e(
                            sender_name="DocuSign",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Wave: signature required today — DPA-3510",
                            body=f"Sign:\nhttp://{docs_spoof}/sign/dpa-3510\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/sign/dpa-3510"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # -------------------------
        # LEVEL 18 (HL)
        # -------------------------
        if level_no == 18:
            defs.append(
                dict(
                    scenario=scenario,
                    number=18,
                    title="Financial exploitation: customs + carriers + bank changes (Sophos degraded)",
                    briefing=(
                        "Attackers pivot to money and logistics. Customs/carrier refs are being used to spear phish. "
                        "Sophos degraded. Expect 2 spear phish max: one carrier/customs, one finance/bank-change."
                    ),
                    scenario_overrides=level_overrides.get(18, {}),
                    base_emails=[
                        e(
                            sender_name="Security Operations",
                            sender_email=f"soc@{dom}",
                            subject="Incident guidance: phishing volume elevated — verify portals manually",
                            body="Do not use emailed login links. Navigate to portals directly and report suspicious emails.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/incident/INC-2026-09/guidance"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Status: Sophos email filtering degraded — increased risk",
                            body="Treat unexpected customs/courier emails as suspicious. Use internal portals.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/sophos-degraded"],
                            attachments=[],
                        ),
                        e(
                            sender_name="AM Shift Lead (Callum Price)",
                            sender_email=f"callum.price@{dom}",
                            subject="Shift cover: 1 driver no-show + 1 sickness — authorise agency cover?",
                            body="We’ll miss slots if we don’t cover. Can you authorise 2 agency drivers?",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Absence cases: record cover arrangements (portal)",
                            body="Please confirm cover arrangements and minimise personal details in email.",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[f"{hr_portal}/absence/cases?dept=depot-ops&context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Relations",
                            sender_email=f"carriers@{dom}",
                            subject="Carrier slot SL-2044 at risk — reschedule in portal",
                            body="Reschedule via portal or penalty applies.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/logistics/carriers/slots/reschedule?ref=SL-2044"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Broker (NorthGate)",
                            sender_email="ops@northgatebrokerage.co.uk",
                            subject="Shipment HL-8122: customs request for clarification",
                            body="Customs wants clarification on commodity description. Please confirm wording.",
                            is_phish=False,
                            difficulty=5,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="HL-8122: upload broker response (portal)",
                            body="Upload broker response/supporting docs in customs portal.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/customs/shipments/HL-8122"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Procurement System",
                            sender_email=f"no-reply@{dom}",
                            subject="Vendor bank change request logged: BC-5101 (verification required)",
                            body="Bank change requires verification steps before approval.",
                            is_phish=False,
                            difficulty=5,
                            category="procurement",
                            links=[f"{vendor_portal}/bank-changes/verify?case=BC-5101"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Finance Ops",
                            sender_email=f"finance-ops@{dom}",
                            subject="Policy reminder (incident): bank changes must be verified (PDF attached)",
                            body="No exceptions during incident periods.",
                            is_phish=False,
                            difficulty=5,
                            category="finance",
                            links=[],
                            attachments=["Bank_Change_Policy_IncidentWeek.pdf"],
                        ),
                        e(
                            sender_name="Fleet Coordinator (Rory Sinclair)",
                            sender_email=f"rory.sinclair@{dom}",
                            subject="Fuel card: emergency re-issue request needs approval (portal)",
                            body="Portal request raised. Needs your approval.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/fleet/fuelcards/requests/HL-29?context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities",
                            sender_email=f"facilities@{dom}",
                            subject="Forklift maintenance moved — acknowledge schedule (portal)",
                            body="Please acknowledge schedule change so we can plan bay access.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/maintenance/forklift?week=current&update=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Incident week reminder: no approvals via email — log rationale in notes portal",
                            body="Keep audit notes up to date. Escalate anything suspicious before acting.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/portal/notes/depot-ops?context=incident"],
                            attachments=[],
                        ),
                        # ---- spear phish 1 (carrier slot) ----
                        e(
                            sender_name="Carrier Portal Notifications",
                            sender_email=f"no-reply@{slug}-tracking.com",
                            subject="SL-2044: reschedule confirmed — sign in to approve penalty waiver",
                            body=(
                                "Penalty waiver requires manager approval within 30 minutes:\n"
                                f"http://{slug}-tracking.com/waiver/approve?ref=SL-2044\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{slug}-tracking.com/waiver/approve?ref=SL-2044"],
                            attachments=[],
                        ),
                        # ---- spear phish 2 (bank change evidence) ----
                        e(
                            sender_name="Finance Controls",
                            sender_email=f"controls@{finance_spoof}",
                            subject="BC-5101: verification evidence missing — upload now to release approvals",
                            body=(
                                "Verification evidence for BC-5101 is missing.\n"
                                "Upload evidence to release approvals:\n"
                                f"http://{finance_spoof}/controls/evidence/upload?case=BC-5101\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{finance_spoof}/controls/evidence/upload?case=BC-5101"],
                            attachments=[],
                        ),
                        # additional phish noise (non-spear)
                        e(
                            sender_name="IT Wi-Fi Team",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="Depot devices list needed — upload via secure form",
                            body=f"Upload:\nhttp://{helpdesk_spoof}/forms/device-list\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/forms/device-list"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Invoice",
                            sender_email=f"customs@{docs_spoof}",
                            subject="HL-8122: customs fee invoice attached — pay to release",
                            body="Invoice attached for release.",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[],
                            attachments=["CustomsFee_HL-8122.pdf"],
                        ),
                        e(
                            sender_name="Agency Staffing",
                            sender_email="ops@fastcoverstaffing.co.uk",
                            subject="Re: agency drivers — rates attached",
                            body="Rates attached. Confirm 2 drivers for AM shift and PO contact.",
                            is_phish=False,
                            difficulty=5,
                            category="external",
                            links=[],
                            attachments=["Agency_Rates_AM_IncidentWeek.pdf"],
                        ),
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="HL-8122: broker response uploaded — approve submission (portal)",
                            body="Approve submission so the case can proceed.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/customs/shipments/HL-8122/approve"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Relations",
                            sender_email=f"carriers@{dom}",
                            subject="Penalty risk: SL-2044 not rescheduled by 14:00",
                            body="Please reschedule in portal to avoid auto-penalty.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/logistics/carriers/slots/reschedule?ref=SL-2044&urgent=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Vendor: FuelCards Ltd",
                            sender_email="support@fuelcards-ltd.co.uk",
                            subject="Re: HL-29 fuel card — we need confirmation of authorised contact",
                            body="Please confirm authorised contact details via your official portal route.",
                            is_phish=False,
                            difficulty=5,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="Wave: HL-8122 release window today — approval needed",
                            body="If we miss today’s window, release shifts to tomorrow.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/customs/shipments/HL-8122/approve?window=today"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Relations",
                            sender_email=f"carriers@{dom}",
                            subject="Wave: SL-2044 escalated — slot will be cancelled if not updated",
                            body="Update slot in portal within 45 minutes.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/logistics/carriers/slots/reschedule?ref=SL-2044&escalation=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Banking Alerts",
                            sender_email=f"alerts@{bank_spoof}",
                            subject="Wave: unusual beneficiary verification pending — re-authenticate",
                            body=f"Re-auth:\nhttp://{bank_spoof}/reauth/beneficiary\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{bank_spoof}/reauth/beneficiary"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # -------------------------
        # LEVEL 19 (KU)
        # -------------------------
        if level_no == 19:
            defs.append(
                dict(
                    scenario=scenario,
                    number=19,
                    title="Event week under breach conditions: identity confusion + portal spoofing",
                    briefing=(
                        "Kestrel’s event week continues under breach guidance. Sophos degraded. "
                        "Expect portal-spoofing and identity confusion. 1–2 spear phish max."
                    ),
                    scenario_overrides=level_overrides.get(19, {}),
                    base_emails=[
                        e(
                            sender_name="Information Security",
                            sender_email=f"infosec@{dom}",
                            subject="Incident notice: heightened phishing risk — use portals directly (portal)",
                            body="Do not enter credentials from emailed links. Use official portals and report suspicious mail.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/incident/INC-2026-11/guidance"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Status: Sophos email filtering degraded",
                            body="Expect phishing. Portal maintenance continues as scheduled.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/sophos-degraded"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Events Team",
                            sender_email=f"events@{dom}",
                            subject="EV-1041: guest pass list due today (portal upload)",
                            body="Upload guest names via facilities portal. Do not email names externally.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/events/guest-passes/upload?event=EV-1041"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="EV-1041: AV delivery — confirm loading bay slot",
                            body="Confirm slot and contact for handover in portal.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/deliveries/confirm?ref=EV-AV-311"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Timetabling",
                            sender_email=f"timetabling@{dom}",
                            subject="Room change posted — notify staff (portal)",
                            body="Room change posted. Please notify affected staff.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/portal/timetabling/changes?week=current&event=EV-1041"],
                            attachments=[],
                        ),
                        e(
                            sender_name="School Finance",
                            sender_email=f"school-finance@{dom}",
                            subject="Invoice received: AV-6022 (PDF attached) — confirm cost centre",
                            body="Invoice attached. Please confirm cost centre and approval route.",
                            is_phish=False,
                            difficulty=5,
                            category="finance",
                            links=[],
                            attachments=["AV-6022.pdf"],
                        ),
                        e(
                            sender_name="Research Office",
                            sender_email=f"research-office@{dom}",
                            subject="Compliance check: RC-2012 responses due today (portal)",
                            body="Please respond in portal. Follow-up required for closure.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/research/compliance/checks/RC-2012?due=today"],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Pay query routing reminder (portal)",
                            body="Pay queries must be logged in HR portal. Avoid emailing personal details.",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[f"{hr_portal}/pay/help?context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Guest Services",
                            sender_email=f"guestservices@{dom}",
                            subject="EV-1041: VIP arrival schedule — confirm (portal)",
                            body="Confirm arrival schedule so security can prepare.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/events/EV-1041/vip-schedule"],
                            attachments=[],
                        ),
                        # spear phish 1: guest list / facilities portal spoof
                        e(
                            sender_name="University SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="EV-1041: Guest_Access_List.xlsx shared with you (open)",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=EV-1041-guestlist\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{sharepoint_spoof}/open?id=EV-1041-guestlist"],
                            attachments=[],
                        ),
                        # optional spear phish 2 (keep to 2 max): payroll adjustment referencing HR reminders
                        e(
                            sender_name="HR Portal Notifications",
                            sender_email=f"no-reply@{payroll_spoof}",
                            subject="Pay query case requires verification — EV-week adjustment pending",
                            body=f"Verify:\nhttp://{payroll_spoof}/pay/verify?case=PAY-11802\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{payroll_spoof}/pay/verify?case=PAY-11802"],
                            attachments=[],
                        ),
                        # additional realism / noise
                        e(
                            sender_name="IT Service Desk",
                            sender_email=f"support@{dom}",
                            subject="EV-1041: temporary guest Wi-Fi codes available (portal)",
                            body="Codes available in portal; do not share externally.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/wifi/guest-codes?event=EV-1041"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Colleague (Sam)",
                            sender_email=f"sam.walters@{dom}",
                            subject="Promo slide: do you want last year’s clip again?",
                            body=f"Internal clip link:\n{docs_portal}/shared/clip?id=promo-2023\n",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"{docs_portal}/shared/clip?id=promo-2023"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Secure Document",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Document shared: EV-1041_Room_Changes.docm",
                            body=f"Download:\nhttp://{docs_spoof}/download?id=ev-1041-room-changes\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/download?id=ev-1041-room-changes"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Fire marshal note: occupancy reminder for updated room",
                            body="Confirm occupancy limits in portal for the updated room assignment.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/rooms/occupancy?room=H3.12&event=EV-1041"],
                            attachments=[],
                        ),
                        e(
                            sender_name="External Vendor (AV)",
                            sender_email="ops@brightwave-av.co.uk",
                            subject="EV-1041 delivery confirmation — please confirm delivery contact",
                            body="Please confirm delivery contact via your official process (no personal data by email).",
                            is_phish=False,
                            difficulty=5,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Research Office",
                            sender_email=f"research-office@{dom}",
                            subject="Reminder: RC-2012 requires final response for closure (portal)",
                            body="Reminder — respond in portal to close the case.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[f"https://{dom}/research/compliance/checks/RC-2012?status=open"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Events Team",
                            sender_email=f"events@{dom}",
                            subject="Wave: EV-1041 guest list incomplete — security needs it within 1 hour",
                            body="Please upload final list ASAP via portal.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[f"{facilities_portal}/events/guest-passes/upload?event=EV-1041&urgent=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Wave: portal maintenance moved earlier (status)",
                            body="Maintenance now starts at 21:00. See status page.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"{it_portal}/status/maintenance?update=1&context=incident"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Guest Services",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="Wave: VIP schedule verification required (secure link)",
                            body=f"Verify:\nhttp://{helpdesk_spoof}/vip/verify?event=EV-1041\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/vip/verify?event=EV-1041"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # -------------------------
        # LEVEL 20 (NB) — FINAL
        # -------------------------
        defs.append(
            dict(
                scenario=scenario,
                number=20,
                title="Final boss: breach fallout + audit + supplier fraud + SSO instability",
                briefing=(
                    "Maximum realism and overload. Breach fallout, audit evidence, vendor pressure, banking verification, "
                    "HR issues and IT instability overlap. Sophos filtering degraded. Expect 2 spear phish max that "
                    "closely match live threads."
                ),
                scenario_overrides=level_overrides.get(20, {}),
                base_emails=[
                    e(
                        sender_name="Incident Command",
                        sender_email=f"incident-command@{dom}",
                        subject="INC-2026-04: daily objectives + comms discipline (portal)",
                        body="Daily objectives posted. Use incident portal only for incident details and evidence.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[f"{incident_portal}/objectives?day=today&ref=INC-2026-04"],
                        attachments=[],
                    ),
                    e(
                        sender_name="IT Status",
                        sender_email=f"it-status@{dom}",
                        subject="Incident: intermittent SSO failures continuing (status)",
                        body="SSO intermittent. Use status page for guidance. Do not use emailed re-login links.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"{it_portal}/status/sso-incident?context=incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Security Operations",
                        sender_email=f"soc@{dom}",
                        subject="Advisory: spear phishing exploiting active incident threads",
                        body="Assume attackers know your case IDs. Verify requests via portals and call-backs only.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[f"{incident_portal}/guidance/spear-phishing"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Internal Audit",
                        sender_email=f"audit@{dom}",
                        subject="Audit sample: bank change evidence pack request (portal upload) — deadline EOD",
                        body="Upload evidence packs for bank changes approved/attempted this week. Deadline EOD.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"{finance_portal}/audit/evidence/upload?topic=bank-changes&ref=INC-2026-04"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Legal Ops",
                        sender_email=f"legal@{dom}",
                        subject="Disclosure workflow: do not send incident docs by email (portal only)",
                        body="All draft disclosures and regulator comms must remain in the legal portal.",
                        is_phish=False,
                        difficulty=5,
                        category="legal",
                        links=[f"https://{dom}/legal/incident/INC-2026-04/workflow"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Finance Controls",
                        sender_email=f"controls@{dom}",
                        subject="Controls reminder: bank changes require portal verification + call-back (PDF attached)",
                        body="Reminder attached. No exceptions, even under incident pressure.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[],
                        attachments=["BankChange_Verification_Steps_Incident.pdf"],
                    ),
                    e(
                        sender_name="Procurement System",
                        sender_email=f"no-reply@{dom}",
                        subject="Vendor bank change request: BC-9470 (verification required)",
                        body="Verification required before approval.",
                        is_phish=False,
                        difficulty=5,
                        category="procurement",
                        links=[f"{vendor_portal}/bank-changes/verify?case=BC-9470"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Westridge Supplies",
                        sender_email="billing@westridgesupplies.co.uk",
                        subject="URGENT: payment run today — BC-9470 verification status?",
                        body=(
                            "Hello,\n\nWe have urgent suppliers waiting. Can you confirm when verification call-back can occur?\n"
                            "We submitted BC-9470 in portal.\n\nBilling"
                        ),
                        is_phish=False,
                        difficulty=5,
                        category="supplier",
                        links=[],
                        attachments=[],
                    ),
                    e(
                        sender_name="Finance Ops",
                        sender_email=f"finance-ops@{dom}",
                        subject="Payment run: approvals reopened due to SSO disruption (portal)",
                        body="Approvals reopened. Please re-check queue and record rationale for exceptions.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[f"{finance_portal}/payments/approvals?reopen=1&context=incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Payroll Team",
                        sender_email=f"payroll@{dom}",
                        subject="Payroll run: managers to review exception list (portal) — deadline 16:00",
                        body="Review exception list and flag anomalies by 16:00. No payslips by email.",
                        is_phish=False,
                        difficulty=5,
                        category="hr",
                        links=[f"{hr_portal}/payroll/exceptions?run=monthly&context=incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="HR Shared Services",
                        sender_email=f"hr@{dom}",
                        subject="Leave approval waiting (portal) — keep coverage stable",
                        body="Approve/decline leave in portal. Avoid personal details in email.",
                        is_phish=False,
                        difficulty=5,
                        category="hr",
                        links=[f"{hr_portal}/leave/approvals?team=ops-finance&context=incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Facilities Desk",
                        sender_email=f"facilities@{dom}",
                        subject="Delivery today: replacement desks — confirm bay slot",
                        body="Confirm bay slot and escort contact in portal.",
                        is_phish=False,
                        difficulty=5,
                        category="facilities",
                        links=[f"{facilities_portal}/deliveries/confirm?ref=DESK-9102"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Site Security",
                        sender_email=f"security@{dom}",
                        subject="Visitor list needed for DESK-9102 delivery (portal upload)",
                        body="Upload visitor list via portal. Do not email names externally.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[f"{facilities_portal}/visitors/upload?ref=DESK-9102"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Service Desk",
                        sender_email=f"support@{dom}",
                        subject="Ticket: user locked out during SSO incident (portal)",
                        body="Update ticket with notes once resolved. Use official portal flow.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"{it_portal}/servicedesk/tickets/SD-28901"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Invoice Processing",
                        sender_email=f"invoices@{dom}",
                        subject="Invoice received: INV-26090 (PDF attached)",
                        body="Invoice attached. Please confirm match / exception handling.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[],
                        attachments=["INV-26090.pdf"],
                    ),
                    e(
                        sender_name="Internal Comms",
                        sender_email=f"comms@{dom}",
                        subject="Staff message scheduled: phishing warning + portal-only guidance (portal)",
                        body="Message drafted. Please review tone and clarity before posting.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"https://{dom}/comms/incident/phishing-warning?ref=INC-2026-04"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Jordan Reeves",
                        sender_email=f"jordan.reeves@{dom}",
                        subject="BC-9470 evidence pack: I’ve got call notes + screenshots ready",
                        body="Once you confirm the right upload location, I’ll submit.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[],
                        attachments=[],
                    ),
                    e(
                        sender_name=scenario.line_manager_name,
                        sender_email=mgr_email,
                        subject="Incident day: approve fast, document faster — escalate anything odd",
                        body="If anything looks off, pause and escalate. Keep audit notes current.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"https://{dom}/portal/notes/ops-finance?day=today&context=incident"],
                        attachments=[],
                    ),
                    # ---- spear phish 1 (banking verification) ----
                    e(
                        sender_name="Banking Alerts",
                        sender_email=f"alerts@{bank_spoof}",
                        subject="BC-9470: beneficiary flagged — re-authenticate to release payment",
                        body=f"Re-authenticate:\nhttp://{bank_spoof}/reauth/release?case=BC-9470\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{bank_spoof}/reauth/release?case=BC-9470"],
                        attachments=[],
                    ),
                    # ---- spear phish 2 (audit/legal doc request) ----
                    e(
                        sender_name="Legal Ops",
                        sender_email=f"legal@{docs_spoof}",
                        subject="INC-2026-04: audit evidence pack requires signature acknowledgement",
                        body=(
                            "Acknowledgement required for evidence pack submission:\n"
                            f"http://{docs_spoof}/ack/evidence?ref=INC-2026-04\n"
                        ),
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{docs_spoof}/ack/evidence?ref=INC-2026-04"],
                        attachments=[],
                    ),
                    # extra non-spear phish noise
                    e(
                        sender_name="IT SSO Team",
                        sender_email=f"no-reply@{helpdesk_spoof}",
                        subject="SSO fix: immediate re-login required",
                        body=f"Re-login:\nhttp://{helpdesk_spoof}/sso/relogin\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{helpdesk_spoof}/sso/relogin"],
                        attachments=[],
                    ),
                    e(
                        sender_name=f"{scenario.company_name} SharePoint",
                        sender_email=f"no-reply@{sharepoint_spoof}",
                        subject="Shared: BankChange_Confirmation_BC-9470.pdf (open)",
                        body=f"Open:\nhttp://{sharepoint_spoof}/open?id=BC-9470-confirm\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{sharepoint_spoof}/open?id=BC-9470-confirm"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Procurement Portal",
                        sender_email=f"no-reply@{dom}",
                        subject="Vendor profile update: contact details amended (portal)",
                        body="Review vendor contact changes (not bank) in portal.",
                        is_phish=False,
                        difficulty=5,
                        category="procurement",
                        links=[f"{vendor_portal}/changes/pending?case=VND-6311"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Facilities Desk",
                        sender_email=f"facilities@{dom}",
                        subject="Reminder: escort needed for DESK-9102 at 12:10",
                        body="Please confirm escort in portal.",
                        is_phish=False,
                        difficulty=5,
                        category="facilities",
                        links=[f"{facilities_portal}/deliveries/confirm?ref=DESK-9102&reminder=1"],
                        attachments=[],
                    ),
                ],
                wave_emails=[
                    e(
                        sender_name="Finance Ops",
                        sender_email=f"finance-ops@{dom}",
                        subject="Wave: payment cut-off moved earlier (15:15) due to incident constraints",
                        body="Please finalise approvals early and keep evidence trail updated.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[f"{finance_portal}/payments/approvals?cutoff=1515&context=incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Internal Audit",
                        sender_email=f"audit@{dom}",
                        subject="Wave: evidence pack reminder — bank changes sample due in 2 hours",
                        body="Reminder: upload evidence packs to portal for today’s sample.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"{finance_portal}/audit/evidence/upload?topic=bank-changes&reminder=1"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Incident Command",
                        sender_email=f"incident-command@{dom}",
                        subject="Wave: attackers spoofing incident command — verify sender carefully",
                        body="If unsure, cross-check in portal and report suspicious mail.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[f"{incident_portal}/updates?ref=INC-2026-04&update=phish-spoofing"],
                        attachments=[],
                    ),
                ],
            )
        )

    return defs