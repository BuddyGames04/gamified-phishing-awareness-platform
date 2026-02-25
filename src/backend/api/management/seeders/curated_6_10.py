from __future__ import annotations

from typing import Any

from api.management.seeders.common import domain_for_company, slugify_company


def curated_levels_6_10(scenario_by_company) -> list[dict[str, Any]]:
    """
    Levels 6–10: fully curated (handmade), no procedural generation.
    Intentional inconsistency in level length:
      - L6–7: 6–8 base emails, 1–2 wave
      - L8–10: 9–12 base emails, 2–3 wave
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
        6: nb,
        7: hl,
        8: nb,
        9: rs,
        10: ku,
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
        return dict(**kwargs)

    defs: list[dict[str, Any]] = []

    for level_no, scenario in mapping.items():
        dom = domain_for_company(scenario.company_name)
        mgr_email = f"{clean_mgr_name(scenario.line_manager_name)}@{dom}"
        slug = slugify_company(scenario.company_name)

        sharepoint_spoof = f"{slug}-sharepoint.com"
        payments_spoof = f"{slug}-payments.com"
        helpdesk_spoof = f"{slug}-helpdesk.com"
        docs_spoof = f"{slug}-docs.com"
        finance_spoof = f"{slug}-finance.com"

        # ------------------------
        # LEVEL 6 (6 base, 1 wave)
        # ------------------------
        if level_no == 6:
            defs.append(
                dict(
                    scenario=scenario,
                    number=6,
                    title="Supplier follow-ups and portal hygiene",
                    briefing=(
                        "Slightly more volume than Level 5. Supplier chasers and internal requests increase. "
                        "Stay consistent: use approved portals and verify changes."
                    ),
                    base_emails=[
                        e(
                            sender_name="Procurement Team",
                            sender_email=f"procurement@{dom}",
                            subject="Approved supplier list update (PDF attached)",
                            body="Hi,\n\nAttached is the updated approved supplier list.\n\nThanks,\nProcurement",
                            is_phish=False,
                            difficulty=2,
                            category="internal",
                            links=[],
                            attachments=["Approved_Suppliers_Update.pdf"],
                        ),
                        e(
                            sender_name="Invoice Processing",
                            sender_email=f"invoices@{dom}",
                            subject="Invoice received: INV-21102 (PDF attached)",
                            body="Hi,\n\nNew invoice attached. Please process within policy timeframes.\n\nRegards,\nInvoice Processing",
                            is_phish=False,
                            difficulty=2,
                            category="finance",
                            links=[],
                            attachments=["INV-21102.pdf"],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Can you update today’s notes in the portal?",
                            body=(
                                f"Hi,\n\nPlease log today’s actions/decisions in the portal notes.\n\n"
                                f"Thanks,\n{scenario.line_manager_name}"
                            ),
                            is_phish=False,
                            difficulty=2,
                            category="internal",
                            links=[f"https://{dom}/finance/notes/today"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Westridge Supplies",
                            sender_email="billing@westridgesupplies.co.uk",
                            subject="Overdue invoice reminder (statement attached)",
                            body="Hello,\n\nAttached statement for overdue items. Could you confirm expected payment date?\n\nThanks,\nBilling",
                            is_phish=False,
                            difficulty=2,
                            category="supplier",
                            links=[],
                            attachments=["Westridge_Statement.pdf"],
                        ),
                        e(
                            sender_name=f"{scenario.company_name} SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared file: Remittance_Template.xlsx (open link)",
                            body=(
                                "A file has been shared with you.\n\n"
                                f"Open:\nhttp://{sharepoint_spoof}/open?id=remit-template\n"
                            ),
                            is_phish=True,
                            difficulty=3,
                            category="phish",
                            links=[f"http://{sharepoint_spoof}/open?id=remit-template"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Supplier Payments",
                            sender_email=f"payments@{payments_spoof}",
                            subject="Bank details update required (verify)",
                            body=(
                                "Hello,\n\nWe updated our bank details. Verify here to avoid failed payments:\n"
                                f"http://{payments_spoof}/confirm\n"
                            ),
                            is_phish=True,
                            difficulty=3,
                            category="phish",
                            links=[f"http://{payments_spoof}/confirm"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Accounts Team",
                            sender_email=f"accounts@{dom}",
                            subject="Follow-up: approvals needed for payment run (portal)",
                            body="Hi,\n\nApprovals are pending for today’s payment run. Please review in the portal.\n\nThanks,\nAccounts",
                            is_phish=False,
                            difficulty=3,
                            category="finance",
                            links=[f"https://{dom}/finance/payments/approvals"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # ------------------------
        # LEVEL 7 (8 base, 2 wave)
        # ------------------------
        if level_no == 7:
            defs.append(
                dict(
                    scenario=scenario,
                    number=7,
                    title="Controls under pressure: evidence and escalation",
                    briefing=(
                        "A step up in volume and conflicting cues. Document actions, follow verification steps, "
                        "and escalate anything suspicious."
                    ),
                    base_emails=[
                        e(
                            sender_name="Internal Audit",
                            sender_email=f"audit@{dom}",
                            subject="Audit request: evidence list (PDF attached)",
                            body="Hi,\n\nPlease provide an evidence trail for the attached list by end of day.\n\nThanks,\nAudit",
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[],
                            attachments=["Audit_Evidence_List.pdf"],
                        ),
                        e(
                            sender_name="Operations",
                            sender_email=f"operations@{dom}",
                            subject="Request: confirm delivery ETA (portal link)",
                            body="Hi,\n\nCan you confirm ETA in the logistics portal and reply with the latest update?\n\nThanks,\nOperations",
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[f"https://{dom}/logistics/eta"],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Please keep notes for anything unusual (portal)",
                            body=(
                                "Hi,\n\nIf anything looks off, log it in the portal notes and escalate before actioning.\n\n"
                                f"Thanks,\n{scenario.line_manager_name}"
                            ),
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[f"https://{dom}/portal/notes"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Supplier Quotes",
                            sender_email="sales@packaging-direct.co.uk",
                            subject="Quote attached (Ref Q-2219)",
                            body="Hi,\n\nPlease find our quote attached.\n\nKind regards,\nSales",
                            is_phish=False,
                            difficulty=3,
                            category="supplier",
                            links=[],
                            attachments=["Quote_Q-2219.pdf"],
                        ),
                        e(
                            sender_name="Procurement System",
                            sender_email=f"no-reply@{dom}",
                            subject="PO created: PO-88017 (PDF attached)",
                            body="A new purchase order has been created. PDF attached for records.",
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[],
                            attachments=["PO-88017.pdf"],
                        ),
                        e(
                            sender_name="Courier Updates",
                            sender_email=f"no-reply@{slug}-tracking.com",
                            subject="Delivery issue — confirm slot",
                            body=f"Please confirm a new delivery slot:\nhttp://{slug}-tracking.com/confirm-slot\n",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[f"http://{slug}-tracking.com/confirm-slot"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Vendor Portal",
                            sender_email=f"no-reply@{payments_spoof}",
                            subject="Secure message: action required to view vendor note",
                            body=f"Secure login:\nhttp://{payments_spoof}/login\n",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[f"http://{payments_spoof}/login"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Paperwork",
                            sender_email=f"customs@{docs_spoof}",
                            subject="Customs invoice attached — action required",
                            body="Customs invoice attached. Please open and confirm details.",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[],
                            attachments=["CustomsInvoice_88017.pdf.scr"],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Payments Desk",
                            sender_email=f"payments@{dom}",
                            subject="Reminder: bank changes require verification (PDF attached)",
                            body="Hi,\n\nReminder: bank changes must be verified via approved process.\n\nPayments Desk",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["BankChange_Verification_Policy.pdf"],
                        ),
                        e(
                            sender_name="Supplier Portal Support",
                            sender_email=f"support@{helpdesk_spoof}",
                            subject="Account alert: verify to avoid suspension",
                            body=f"Unusual login attempts detected.\nVerify now:\nhttp://{helpdesk_spoof}/verify\n",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/verify"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # ------------------------
        # LEVEL 8 (10 base, 2 wave)
        # ------------------------
        if level_no == 8:
            defs.append(
                dict(
                    scenario=scenario,
                    number=8,
                    title="Quarter-end close: higher volume, better phish",
                    briefing=(
                        "Quarter-end starts. Volume increases and phish becomes more convincing. "
                        "Expect supplier chasers, internal approvals, and portal spoofing."
                    ),
                    base_emails=[
                        e(
                            sender_name="Finance Ops",
                            sender_email=f"finance-ops@{dom}",
                            subject="Quarter-end close checklist (portal)",
                            body="Hi,\n\nClose checklist is available in the portal. Please work through it today.\n\nFinance Ops",
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[f"https://{dom}/finance/close/checklist"],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Prioritise vendor chasers today",
                            body=(
                                "Hi,\n\nPlease prioritise vendor chasers today. Flag anything suspicious before actioning.\n\n"
                                f"Thanks,\n{scenario.line_manager_name}"
                            ),
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[f"https://{dom}/finance/close/priorities"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Accounts Team",
                            sender_email=f"accounts@{dom}",
                            subject="Payment run: approvals needed (portal)",
                            body="Hi,\n\nApprovals needed before 16:00. Please review the queue.\n\nThanks,\nAccounts",
                            is_phish=False,
                            difficulty=3,
                            category="finance",
                            links=[f"https://{dom}/finance/payments/approvals"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Invoice Processing",
                            sender_email=f"invoices@{dom}",
                            subject="Invoice received: INV-21240 (PDF attached)",
                            body="Hi,\n\nInvoice attached. Please process according to policy.\n\nInvoice Processing",
                            is_phish=False,
                            difficulty=3,
                            category="finance",
                            links=[],
                            attachments=["INV-21240.pdf"],
                        ),
                        e(
                            sender_name="Internal Audit",
                            sender_email=f"audit@{dom}",
                            subject="Quarter-end sample guidance (PDF attached)",
                            body="Hi,\n\nPlease see attached guidance for sample requests. No action required yet.\n\nThanks,\nAudit",
                            is_phish=False,
                            difficulty=3,
                            category="internal",
                            links=[],
                            attachments=["Audit_Sample_Guidance.pdf"],
                        ),
                        e(
                            sender_name="Westridge Supplies",
                            sender_email="billing@westridgesupplies.co.uk",
                            subject="RE: statement request (attached)",
                            body="Hello,\n\nAttached statement for outstanding items. Please confirm expected payment date.\n\nThanks,\nBilling",
                            is_phish=False,
                            difficulty=3,
                            category="supplier",
                            links=[],
                            attachments=["Westridge_Statement_QE.pdf"],
                        ),
                        e(
                            sender_name=f"{scenario.company_name} SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared file: Close_Schedule.xlsx (open link)",
                            body=(
                                "A file has been shared with you.\n\n"
                                f"Open:\nhttp://{sharepoint_spoof}/open?id=close-schedule\n"
                            ),
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[f"http://{sharepoint_spoof}/open?id=close-schedule"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Finance Shared Drive",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Document: Vendor_Master_Update.xlsm (download)",
                            body=f"Download:\nhttp://{docs_spoof}/download?v=vendor-master\n",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[f"http://{docs_spoof}/download?v=vendor-master"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Voice Mail",
                            sender_email=f"voicemail@{helpdesk_spoof}",
                            subject="New voicemail received (open attachment)",
                            body="You received a new voicemail.\n\nOpen the attachment to listen.",
                            is_phish=True,
                            difficulty=4,
                            category="phish",
                            links=[],
                            attachments=["Voicemail_90218.htm"],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Notice: finance portal slowness (status page)",
                            body="Hi,\n\nWe’re investigating intermittent slowness on the finance portal.\n\nIT",
                            is_phish=False,
                            difficulty=3,
                            category="it",
                            links=[f"https://{dom}/it/status/finance-portal"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Accounts Team",
                            sender_email=f"accounts@{dom}",
                            subject="FOLLOW-UP: payment approvals reopened (portal)",
                            body="Hi,\n\nWe reopened approvals due to late updates. Please re-check the queue.\n\nAccounts",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[f"https://{dom}/finance/payments/approvals?reopen=1"],
                            attachments=[],
                        ),
                        e(
                            sender_name="CFO Office",
                            sender_email=f"cfo@{finance_spoof}",
                            subject="Urgent: settle supplier today — confirm via link",
                            body=f"Confirm:\nhttp://{finance_spoof}/confirm?action=pay\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{finance_spoof}/confirm?action=pay"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # ------------------------
        # LEVEL 9 (11 base, 3 wave)
        # ------------------------
        if level_no == 9:
            defs.append(
                dict(
                    scenario=scenario,
                    number=9,
                    title="Authority conflict: exec spoof + thread pressure",
                    briefing=(
                        "High volume. Mixed legit + polished phish. Conflicting authority signals appear. "
                        "Keep thread hygiene and follow verification."
                    ),
                    base_emails=[
                        e(
                            sender_name="Service Desk System",
                            sender_email=f"no-reply@{dom}",
                            subject="Ticket assigned: access request (portal)",
                            body="Ticket assigned. Please update status in the service portal.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"https://{dom}/servicedesk/tickets/SD-21904"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Security",
                            sender_email=f"security@{dom}",
                            subject="Security bulletin: exec spoof attempts (PDF attached)",
                            body="Hi,\n\nSee attached bulletin for recent exec spoof examples.\n\nSecurity",
                            is_phish=False,
                            difficulty=4,
                            category="security",
                            links=[],
                            attachments=["Security_Bulletin_ExecSpoof.pdf"],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Reminder: log actions + rationale (portal)",
                            body=(
                                "Hi,\n\nPlease log what you did + why in the portal notes.\n\n"
                                f"Thanks,\n{scenario.line_manager_name}"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/it/notes"],
                            attachments=[],
                        ),
                        e(
                            sender_name="CI System",
                            sender_email=f"ci@{dom}",
                            subject="Build failure: main branch (portal link)",
                            body="Build failed on main. Please review logs in the CI portal.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"https://{dom}/engineering/ci/builds/last-fail"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Repo Admin",
                            sender_email=f"repo-admin@{dom}",
                            subject="Access review requested (PDF attached)",
                            body="Hi,\n\nPlease review the attached access review request.\n\nThanks,\nRepo Admin",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[],
                            attachments=["AccessReview_Request.pdf"],
                        ),
                        e(
                            sender_name=f"{scenario.company_name} SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared: AccessReview_Q1.xlsx (open)",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=access-review\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{sharepoint_spoof}/open?id=access-review"],
                            attachments=[],
                        ),
                        e(
                            sender_name="SOC Alerts",
                            sender_email=f"soc-alerts@{helpdesk_spoof}",
                            subject="Immediate action: confirm credentials to stop incident",
                            body=f"Confirm:\nhttp://{helpdesk_spoof}/incident/confirm\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/incident/confirm"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Device Management",
                            sender_email=f"mdm@{dom}",
                            subject="Device enrollment reminder (portal)",
                            body="Reminder: device enrollment outstanding. Complete in portal.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"https://{dom}/it/mdm/enrollment"],
                            attachments=[],
                        ),
                        e(
                            sender_name="VPN Team",
                            sender_email=f"vpn@{helpdesk_spoof}",
                            subject="VPN upgrade: confirm your account",
                            body=f"To complete the VPN upgrade, confirm:\nhttp://{helpdesk_spoof}/vpn/confirm\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/vpn/confirm"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Internal Comms",
                            sender_email=f"comms@{dom}",
                            subject="Reminder: report suspicious emails (PDF attached)",
                            body="Hi,\n\nReminder: report suspicious emails using the internal process.\n\nComms",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[],
                            attachments=["Phishing_Reminder.pdf"],
                        ),
                        e(
                            sender_name="Shared Document",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Shared file: AccessReview_Notes.docm (download)",
                            body=f"Download:\nhttp://{docs_spoof}/download?id=access-notes\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/download?id=access-notes"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Security Operations",
                            sender_email=f"soc@{dom}",
                            subject="Wave: reminder — do not enter credentials from email links (portal)",
                            body="Reminder posted in the security portal. Please review.",
                            is_phish=False,
                            difficulty=5,
                            category="security",
                            links=[f"https://{dom}/security/reminders/email-links"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Admin Portal",
                            sender_email=f"admin@{helpdesk_spoof}",
                            subject="Wave: MFA enrollment expiring",
                            body=f"Re-enroll to avoid lockout:\nhttp://{helpdesk_spoof}/mfa/re-enroll\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/mfa/re-enroll"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Service Desk System",
                            sender_email=f"no-reply@{dom}",
                            subject="Wave: ticket SLA risk (portal)",
                            body="Ticket approaching SLA. Please update status in portal.",
                            is_phish=False,
                            difficulty=5,
                            category="it",
                            links=[f"https://{dom}/servicedesk/queues/sla-risk"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        # ------------------------
        # LEVEL 10 (12 base, 3 wave)
        # ------------------------
        defs.append(
            dict(
                scenario=scenario,
                number=10,
                title="Incident day: overload + multi-thread attempts",
                briefing=(
                    "Peak volume. Legit comms get messy while phish stays polished. "
                    "Multiple waves simulate pressure — keep discipline."
                ),
                base_emails=[
                    e(
                        sender_name="Registry",
                        sender_email=f"registry@{dom}",
                        subject="Timetable update available (portal)",
                        body="Hi,\n\nYour timetable has been updated. Please check the portal.\n\nRegistry",
                        is_phish=False,
                        difficulty=5,
                        category="education",
                        links=[f"https://{dom}/portal/timetable"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Research Office",
                        sender_email=f"research-office@{dom}",
                        subject="Travel request submitted (PDF attached)",
                        body="Hi,\n\nTravel request submitted. Attached summary for your records.\n\nResearch Office",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[],
                        attachments=["Travel_Request_Summary.pdf"],
                    ),
                    e(
                        sender_name="Finance Office",
                        sender_email=f"finance@{dom}",
                        subject="Conference registration invoice (PDF attached)",
                        body="Hi,\n\nInvoice attached for conference registration.\n\nFinance",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[],
                        attachments=["Conference_Registration_Invoice.pdf"],
                    ),
                    e(
                        sender_name="IT Status",
                        sender_email=f"it-status@{dom}",
                        subject="Incident: intermittent email delivery delays (status page)",
                        body="Hi,\n\nWe’re investigating intermittent email delivery delays. Track updates here.\n\nIT",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"https://{dom}/it/status/email-delays"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Library Services",
                        sender_email=f"library@{dom}",
                        subject="Reminder: account notice (portal)",
                        body="Hi,\n\nAccount notice posted in the portal.\n\nLibrary Services",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"https://{dom}/portal/notices/library"],
                        attachments=[],
                    ),
                    e(
                        sender_name=f"{scenario.company_name} SharePoint",
                        sender_email=f"no-reply@{sharepoint_spoof}",
                        subject="Shared file: Research_Accounts_List.xlsx (open)",
                        body=f"Open:\nhttp://{sharepoint_spoof}/open?id=research-accounts\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{sharepoint_spoof}/open?id=research-accounts"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Vendor Portal",
                        sender_email=f"no-reply@{docs_spoof}",
                        subject="Document requires signature",
                        body=f"Sign:\nhttp://{docs_spoof}/sign/required\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{docs_spoof}/sign/required"],
                        attachments=[],
                    ),
                    e(
                        sender_name="IT Helpdesk",
                        sender_email=f"support@{dom}",
                        subject="Reminder: report suspicious emails (PDF attached)",
                        body="Hi,\n\nReminder: report suspicious emails using the internal process.\n\nIT Helpdesk",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[],
                        attachments=["Phishing_Report_Process.pdf"],
                    ),
                    e(
                        sender_name="Account Services",
                        sender_email=f"no-reply@{helpdesk_spoof}",
                        subject="Account security notice (verify)",
                        body=f"Confirm your account to avoid restrictions:\nhttp://{helpdesk_spoof}/account/verify\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{helpdesk_spoof}/account/verify"],
                        attachments=[],
                    ),
                    e(
                        sender_name=scenario.line_manager_name,
                        sender_email=mgr_email,
                        subject="Please keep an evidence trail for decisions (portal)",
                        body=(
                            "Hi,\n\nPlease keep an evidence trail for decisions today. Log notes in the portal.\n\n"
                            f"Thanks,\n{scenario.line_manager_name}"
                        ),
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"https://{dom}/portal/notes/decision-trail"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Internal Comms",
                        sender_email=f"comms@{dom}",
                        subject="Policy reminder during incident (PDF attached)",
                        body="Hi,\n\nReminder: follow process during incidents. See attached.\n\nComms",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[],
                        attachments=["Incident_Comms_Guidance.pdf"],
                    ),
                    e(
                        sender_name="Shared Document",
                        sender_email=f"no-reply@{docs_spoof}",
                        subject="Shared file: Updated_Policy.pdf (open)",
                        body=f"Open:\nhttp://{docs_spoof}/open?id=policy\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{docs_spoof}/open?id=policy"],
                        attachments=[],
                    ),
                ],
                wave_emails=[
                    e(
                        sender_name="IT Security",
                        sender_email=f"security@{dom}",
                        subject="Wave: advisory — watch for spoofed portals (PDF attached)",
                        body="Hi,\n\nSee attached advisory with examples of spoofed portals.\n\nSecurity",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[],
                        attachments=["Spoofed_Portal_Advisory.pdf"],
                    ),
                    e(
                        sender_name=f"{scenario.company_name} SharePoint",
                        sender_email=f"no-reply@{sharepoint_spoof}",
                        subject="Wave: shared file — Incident_Day_Exceptions.xlsm",
                        body=f"Open:\nhttp://{sharepoint_spoof}/open?id=incident-exceptions\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{sharepoint_spoof}/open?id=incident-exceptions"],
                        attachments=[],
                    ),
                    e(
                        sender_name="IT Status",
                        sender_email=f"it-status@{dom}",
                        subject="Wave: update — services stabilising (status page)",
                        body="Update posted. Please check the status page for details.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"https://{dom}/it/status/updates"],
                        attachments=[],
                    ),
                ],
            )
        )

    return defs