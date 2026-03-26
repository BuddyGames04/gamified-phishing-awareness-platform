from __future__ import annotations

from typing import Any

from api.management.seeders.common import domain_for_company, slugify_company


def curated_levels_11_15(scenario_by_company) -> list[dict[str, Any]]:

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
        11: nb,
        12: rs,
        13: hl,
        14: ku,
        15: nb,
    }

    level_overrides = {
        11: {
            "role_title": "Operations Finance Lead (Acting)",
            "department_name": "Operations Finance & Supplier Controls",
            "responsibilities": [
                "Own daily payment approvals and exception handling during system transition week.",
                "Manage supplier onboarding checks and bank-detail change verification workflow.",
                "Coordinate with Facilities on urgent deliveries and site access constraints.",
                "Line management: approve leave/sickness, route pay/benefits queries to HR, keep coverage stable.",
                "Team (direct reports):",
                "- Mia Patel (Finance Assistant — invoices & matching)",
                "- Jordan Reeves (Controls Analyst — approvals & audit trail)",
                "- Sana Ahmed (Ops Coordinator — supplier comms & delivery slots)",
            ],
            "intro_text": (
                "It’s a busy week at Northbridge: the finance portal is mid-migration and the operations sites "
                "are receiving critical deliveries. You’re acting as Ops Finance Lead while your manager is in "
                "back-to-back meetings. You’ll receive real internal operational emails (facilities access, "
                "supplier updates, pay questions, sickness requests) alongside normal finance traffic. Multiple "
                "threads will run concurrently; keep an audit trail and verify changes via approved channels."
            ),
        },
        12: {
            "role_title": "Engineering Operations Manager",
            "department_name": "Engineering Operations & Security Enablement",
            "responsibilities": [
                "Coordinate release readiness, vendor tooling renewals, and access governance.",
                "Act as point-of-contact for IT/Sec during incident simulations and credential resets.",
                "Support managers with team admin tasks (sickness notifications, equipment requests, travel).",
                "Maintain evidence trail for procurement + legal review (DPAs, NDAs, renewals).",
                "Team (matrix):",
                "- Priya Nair (Release Coordinator)",
                "- Theo Grant (IT Liaison)",
                "- Elena Volkova (Procurement & Renewals)",
            ],
            "intro_text": (
                "Redwood is in a release-and-renewal crunch: tool renewals, legal paperwork, access reviews, and "
                "incident rehearsal overlap. You’ll get threads that look real (DocuSign-style flows, vendor renewal "
                "notices, password reset requests, internal approvals), plus phish that hijack that context."
            ),
        },
        13: {
            "role_title": "Depot Operations Manager",
            "department_name": "Depot Ops, Fleet & People",
            "responsibilities": [
                "Keep depot running: shift coverage, delivery slots, customs paperwork triage.",
                "Approve sickness/absence and coordinate cover with HR policy constraints.",
                "Handle supplier and carrier comms; verify bank changes and PO amendments.",
                "Escalate security concerns (spoofed customs docs, courier portal resets).",
                "Team (shift leads):",
                "- Callum Price (AM Shift Lead)",
                "- Aisha Khan (PM Shift Lead)",
                "- Rory Sinclair (Fleet Coordinator)",
            ],
            "intro_text": (
                "Harbourline’s depot is under pressure: customs delays, missed delivery windows, and staffing gaps "
                "hit at once. You’ll receive operational emails that feel time-critical (drivers, carriers, HR), "
                "and attackers will exploit that urgency with realistic-looking customs and courier messages."
            ),
        },
        14: {
            "role_title": "School Operations & HR Liaison",
            "department_name": "School Ops, HR Liaison, Finance Support",
            "responsibilities": [
                "Coordinate timetable changes, room moves, and facilities access for events.",
                "Handle HR liaison tasks: sickness notifications, pay queries routing, policy reminders.",
                "Support finance admin for travel, suppliers, and research account compliance.",
                "Manage high email volume during event week; track multiple threads without missing approvals.",
            ],
            "intro_text": (
                "Kestrel is in event week: room changes, guest access, supplier deliveries, travel paperwork, "
                "and HR liaison issues. Multiple threads run simultaneously; phish will look like familiar "
                "university workflows (portals, shared docs, policy acknowledgements)."
            ),
        },
        15: {
            "role_title": "Operations Finance Lead (Acting)",
            "department_name": "Operations Finance & Supplier Controls",
            "responsibilities": [
                "Own daily payment approvals and exception handling during system transition week.",
                "Manage supplier onboarding checks and bank-detail change verification workflow.",
                "Coordinate with Facilities on urgent deliveries and site access constraints.",
                "Line management: approve leave/sickness, route pay/benefits queries to HR, keep coverage stable.",
                "Team (direct reports):",
                "- Mia Patel (Finance Assistant — invoices & matching)",
                "- Jordan Reeves (Controls Analyst — approvals & audit trail)",
                "- Sana Ahmed (Ops Coordinator — supplier comms & delivery slots)",
            ],
            "intro_text": (
                "It’s a busy week at Northbridge: the finance portal is mid-migration and the operations sites "
                "are receiving critical deliveries. You’re acting as Ops Finance Lead while your manager is in "
                "back-to-back meetings. Multiple threads will run concurrently; keep an audit trail and verify "
                "changes via approved channels."
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

        if links and attachments:
            links = []
            kwargs["links"] = []
            kwargs["attachments"] = attachments

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

        sharepoint_spoof = f"{slug}-sharepoint.com"
        helpdesk_spoof = f"{slug}-helpdesk.com"
        docs_spoof = f"{slug}-docs.com"
        finance_spoof = f"{slug}-finance.com"
        payroll_spoof = f"{slug}-payroll.com"
        hr_spoof = f"{slug}-hr.com"
        vendorhub_spoof = f"{slug}-vendorhub.com"
        bank_spoof = f"{slug}-banking.com"

        finance_portal = f"https://{dom}/finance"
        hr_portal = f"https://{dom}/hr"
        it_portal = f"https://{dom}/it"
        facilities_portal = f"https://{dom}/facilities"
        vendor_portal = f"https://{dom}/procurement/vendors"
        docs_portal = f"https://{dom}/portal/docs"

        if level_no == 11:
            defs.append(
                dict(
                    scenario=scenario,
                    number=11,
                    title="Living org: people issues + supplier pressure + facilities access",
                    briefing=(
                        "You’re acting Ops Finance Lead during a migration week. You’ll juggle real operational "
                        "threads (deliveries, sickness, payroll questions) while vendors apply pressure. Phish will "
                        "blend into the context — verify changes via approved portals."
                    ),
                    scenario_overrides=level_overrides.get(11, {}),
                    base_emails=[
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Today: furniture delivery to Ops floor — confirm access window",
                            body=(
                                "Hi,\n\nFacilities confirm furniture delivery is scheduled today 12:30–13:30.\n"
                                "Please confirm loading bay access + escort contact in the facilities portal.\n\n"
                                "Thanks,\nFacilities"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/deliveries/confirm?ref=FURN-4821"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Site Security",
                            sender_email=f"security@{dom}",
                            subject="Visitor access list required for delivery (Ops floor)",
                            body=(
                                "Hi,\n\nPlease upload visitor names + vehicle reg for today’s delivery. "
                                "If unknown, reply with 'TBC' and update by 11:30.\n\nSecurity"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="security",
                            links=[
                                f"{facilities_portal}/visitors/upload?ref=FURN-4821"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Mia Patel",
                            sender_email=f"mia.patel@{dom}",
                            subject="Sick today — migraine (handover attached)",
                            body=(
                                "Hi,\n\nI’ve woken up with a migraine and won’t be able to work today. "
                                "I’ve attached a quick handover of invoices currently waiting on matching.\n\n"
                                "Thanks,\nMia"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[],
                            attachments=["Handover_Invoices_WIP.txt"],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Absence notification received — manager action required (portal)",
                            body="Hi,\n\nPlease record absence details in the HR portal within 24 hours.\n\nHR",
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[f"{hr_portal}/absence/record?employee=mia.patel"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Jordan Reeves",
                            sender_email=f"jordan.reeves@{dom}",
                            subject="Quick one: pay looks off this month — who should I contact?",
                            body=(
                                "Hi,\n\nMy overtime line looks different to last month — not sure if it’s the new "
                                "system. Who should I contact / what’s the process?\n\nThanks,\nJordan"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Payroll Team",
                            sender_email=f"payroll@{dom}",
                            subject="Payroll Q&A: transition week guidance (PDF attached)",
                            body=(
                                "Hi,\n\nDuring transition week, pay queries should be logged via the HR portal.\n"
                                "Guidance attached.\n\nPayroll"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[],
                            attachments=["Payroll_Transition_Week_Guidance.pdf"],
                        ),
                        e(
                            sender_name="Invoice Processing",
                            sender_email=f"invoices@{dom}",
                            subject="Invoice received: INV-23118 (PDF attached)",
                            body="Hi,\n\nInvoice attached for matching. Please process per policy.\n\nInvoices",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["INV-23118.pdf"],
                        ),
                        e(
                            sender_name="Procurement Portal",
                            sender_email=f"no-reply@{dom}",
                            subject="Vendor record update pending approval (portal)",
                            body=(
                                "Hi,\n\nA vendor update is pending approval. Review changes and approve/reject in portal.\n\n"
                                "Procurement System"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="procurement",
                            links=[f"{vendor_portal}/changes/pending?case=VND-1182"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Westridge Supplies",
                            sender_email="billing@westridgesupplies.co.uk",
                            subject="RE: Payment date confirmation — updated remittance details",
                            body=(
                                "Hello,\n\nTo avoid failed remittance, please use our updated bank details on next run.\n"
                                "If you need confirmation, let us know.\n\nThanks,\nBilling"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Notice: finance portal intermittently slow today (status)",
                            body="Hi,\n\nFinance portal may be slow 10:00–14:00 during migration tasks.\n\nIT",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"{it_portal}/status/finance-migration"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Service Desk",
                            sender_email=f"support@{dom}",
                            subject="Ticket update: finance portal permissions (portal)",
                            body="Hi,\n\nYour permissions ticket has been updated. Please review notes.\n\nService Desk",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"{it_portal}/servicedesk/tickets/SD-24110"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Sana Ahmed",
                            sender_email=f"sana.ahmed@{dom}",
                            subject="This made me laugh — clip from yesterday’s site walk 😂",
                            body=(
                                "Quick one — someone clipped the forklift moment from yesterday.\n"
                                "Link here (internal share):\n"
                                f"{docs_portal}/shared/clip?id=sitewalk-vid\n"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"{docs_portal}/shared/clip?id=sitewalk-vid"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Legal Ops",
                            sender_email=f"legal@{dom}",
                            subject="Supplier NDA renewal — confirm approver (portal)",
                            body=(
                                "Hi,\n\nNDA renewal awaiting approver confirmation. Please confirm who should sign.\n\nLegal"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="legal",
                            links=[f"https://{dom}/legal/ndas/NDA-7712"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Payroll Portal",
                            sender_email=f"no-reply@{payroll_spoof}",
                            subject="Revised payslip available — action required to confirm",
                            body=(
                                "A revised payslip has been issued due to transition adjustments.\n"
                                f"Confirm details:\nhttp://{payroll_spoof}/payslip/confirm\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{payroll_spoof}/payslip/confirm"],
                            attachments=[],
                        ),
                        e(
                            sender_name=f"{scenario.company_name} SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared file: Visitor_Access_List.xlsx (delivery) — open",
                            body=(
                                "Visitor access list shared with you for today’s delivery.\n\n"
                                f"Open:\nhttp://{sharepoint_spoof}/open?id=visitor-access-FURN-4821\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{sharepoint_spoof}/open?id=visitor-access-FURN-4821"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="VendorHub Notifications",
                            sender_email=f"no-reply@{vendorhub_spoof}",
                            subject="Vendor change requires immediate confirmation to avoid payment failure",
                            body=(
                                "Vendor record update pending. Confirm to prevent rejected payment.\n"
                                f"http://{vendorhub_spoof}/confirm?v=VND-1182\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{vendorhub_spoof}/confirm?v=VND-1182"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Secure Document",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Document shared: NDA_Renewal_7712.docm",
                            body=f"Download:\nhttp://{docs_spoof}/download?id=nda-7712\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/download?id=nda-7712"],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=f"{clean_mgr_name(scenario.line_manager_name)}@{finance_spoof}",
                            subject="Quick: approve vendor change before 3pm run",
                            body=(
                                "Can you approve the vendor bank change now so we don’t miss the run?\n"
                                f"Use this link:\nhttp://{finance_spoof}/approvals?v=VND-1182\n"
                            ),
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{finance_spoof}/approvals?v=VND-1182"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Wave: delivery moved earlier — confirm escort ASAP",
                            body=(
                                "Update: delivery moved to 12:00 due to driver route. Confirm escort contact now.\n\nFacilities"
                            ),
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/deliveries/confirm?ref=FURN-4821&update=1"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"no-reply@{hr_spoof}",
                            subject="Wave: manager action overdue — absence case will be escalated",
                            body=f"Complete manager action:\nhttp://{hr_spoof}/absence/close\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{hr_spoof}/absence/close"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        if level_no == 12:
            defs.append(
                dict(
                    scenario=scenario,
                    number=12,
                    title="Renewals + legal paperwork + access reviews (thread hijacks)",
                    briefing=(
                        "Release readiness overlaps with renewals and legal docs. You’ll see DPA/NDA threads, "
                        "renewal quotes, access review reminders, and phish that impersonate those exact workflows."
                    ),
                    scenario_overrides=level_overrides.get(12, {}),
                    base_emails=[
                        e(
                            sender_name="Release Coordination",
                            sender_email=f"release@{dom}",
                            subject="Release readiness checklist — sign-off needed (portal)",
                            body="Hi,\n\nChecklist ready for sign-off.\n\nThanks,\nRelease",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[
                                f"https://{dom}/engineering/release/readiness?rel=R-24.3"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="CI System",
                            sender_email=f"ci@{dom}",
                            subject="Build pipeline: performance regression report (PDF attached)",
                            body="Report attached for review before sign-off.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[],
                            attachments=["Pipeline_Performance_Report.pdf"],
                        ),
                        e(
                            sender_name="Procurement & Renewals",
                            sender_email=f"renewals@{dom}",
                            subject="Renewal due: IssueTracker Pro — quote attached",
                            body="Hi,\n\nRenewal quote attached. Please approve route and confirm cost centre.\n\nRenewals",
                            is_phish=False,
                            difficulty=4,
                            category="procurement",
                            links=[f"https://{dom}/procurement/renewals/ITR-9021"],
                            attachments=["IssueTrackerPro_Renewal_Quote.pdf"],
                        ),
                        e(
                            sender_name="Vendor: IssueTracker Pro",
                            sender_email="billing@issuetrackerpro.com",
                            subject="Renewal reminder: contract expires in 14 days",
                            body="Hi,\n\nYour renewal is pending. Please confirm purchase order details.\n\nBilling",
                            is_phish=False,
                            difficulty=4,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Legal Ops",
                            sender_email=f"legal@{dom}",
                            subject="DPA update required for renewal — review clauses (portal)",
                            body="Hi,\n\nDPA update needed. Please review clauses and assign approver.\n\nLegal",
                            is_phish=False,
                            difficulty=4,
                            category="legal",
                            links=[f"https://{dom}/legal/dpa/DPA-3391"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Security Governance",
                            sender_email=f"security@{dom}",
                            subject="Access review window closes Friday — managers to confirm (portal)",
                            body="Hi,\n\nPlease complete access review confirmations.\n\nSecurity",
                            is_phish=False,
                            difficulty=4,
                            category="security",
                            links=[f"https://{dom}/security/access-reviews/AR-7721"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Service Desk",
                            sender_email=f"support@{dom}",
                            subject="MFA enrollment: new policy enforcement next week (portal)",
                            body="Hi,\n\nNew enforcement schedule posted. Please review.\n\nIT",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"https://{dom}/it/mfa/enforcement"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Theo Grant",
                            sender_email=f"theo.grant@{dom}",
                            subject="FYI: vendor keeps asking for 'DPA signed' — can you confirm status?",
                            body="They’re pushing. If we can reply with status + expected sign date that helps.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Travel Desk",
                            sender_email=f"travel@{dom}",
                            subject="Travel itinerary ready — review before ticketing (portal)",
                            body="Hi,\n\nItinerary posted for review.\n\nTravel",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/travel/itineraries/T-5512"],
                            attachments=[],
                        ),
                        e(
                            sender_name="DocuSign",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Signature required: DPA-3391 (expires today)",
                            body=f"Review and sign:\nhttp://{docs_spoof}/sign/dpa-3391\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/sign/dpa-3391"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Security Access Review",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="Access review overdue — confirm credentials to submit",
                            body=f"Submit review:\nhttp://{helpdesk_spoof}/access/submit\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/access/submit"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IssueTracker Pro Billing",
                            sender_email=f"billing@{vendorhub_spoof}",
                            subject="Renewal: payment method update required (to avoid service interruption)",
                            body=f"Update payment method:\nhttp://{vendorhub_spoof}/billing/update\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{vendorhub_spoof}/billing/update\n"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Admin",
                            sender_email=f"admin@{helpdesk_spoof}",
                            subject="MFA enrollment failed — re-authenticate now",
                            body=f"Re-auth:\nhttp://{helpdesk_spoof}/mfa/reauth\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/mfa/reauth"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Elena Volkova",
                            sender_email=f"elena.volkova@{dom}",
                            subject="Renewal approvals: can you confirm which cost centre?",
                            body="Need cost centre and approver name for the PO routing.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Finance Ops",
                            sender_email=f"finance-ops@{dom}",
                            subject="PO created: PO-99281 (PDF attached)",
                            body="PO created. PDF attached for records.",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["PO-99281.pdf"],
                        ),
                        e(
                            sender_name="Vendor: CloudLogs",
                            sender_email="renewals@cloudlogs.io",
                            subject="Contract renewal — confirm renewal term",
                            body="Hi,\n\nPlease confirm 12-month term and billing contact.\n\nThanks,\nCloudLogs",
                            is_phish=False,
                            difficulty=4,
                            category="supplier",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Legal Ops",
                            sender_email=f"legal@{dom}",
                            subject="Reminder: do not sign vendor docs from emailed links (policy)",
                            body="Use internal legal portal for signing workflows.",
                            is_phish=False,
                            difficulty=4,
                            category="legal",
                            links=[f"https://{dom}/legal/policy/signing"],
                            attachments=[],
                        ),
                        e(
                            sender_name="CloudLogs",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Invoice attached: CloudLogs renewal — open to confirm",
                            body="Invoice attached. Open and confirm billing details.",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[],
                            attachments=["CloudLogs_Renewal_Invoice.pdf.scr"],
                        ),
                        e(
                            sender_name="Shared Drive",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared: Release_Readiness_R-24.3.xlsx",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=readiness-R-24.3\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{sharepoint_spoof}/open?id=readiness-R-24.3"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Internal Comms",
                            sender_email=f"comms@{dom}",
                            subject="Reminder: reporting suspicious emails",
                            body="Use the internal reporting button / process in the portal.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/security/reporting"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Release Coordination",
                            sender_email=f"release@{dom}",
                            subject="Wave: sign-off blocked until DPA status confirmed (portal)",
                            body="Please confirm DPA status so sign-off can proceed.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[
                                f"https://{dom}/engineering/release/readiness?rel=R-24.3&block=dpa"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Security Access Review",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="Wave: access review escalation — submit within 2 hours",
                            body=f"Submit:\nhttp://{helpdesk_spoof}/access/submit?escalation=1\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{helpdesk_spoof}/access/submit?escalation=1"
                            ],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        if level_no == 13:
            defs.append(
                dict(
                    scenario=scenario,
                    number=13,
                    title="Depot pressure cooker: customs + shift cover + carrier portals",
                    briefing=(
                        "You’re juggling depot ops: customs delays, carriers rescheduling, sickness cover, "
                        "and supplier bank details. Phish will look like courier/customs workflows."
                    ),
                    scenario_overrides=level_overrides.get(13, {}),
                    base_emails=[
                        e(
                            sender_name="AM Shift Lead (Callum Price)",
                            sender_email=f"callum.price@{dom}",
                            subject="Two drivers reported sick — cover needed",
                            body="Hi,\n\nTwo drivers called in sick. Can we authorise agency cover for AM shift?\n\nCallum",
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Absence cases opened — manager action required (portal)",
                            body="Please confirm absence status and cover arrangements.",
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[f"{hr_portal}/absence/cases?dept=depot-ops"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Fleet Coordinator (Rory Sinclair)",
                            sender_email=f"rory.sinclair@{dom}",
                            subject="Fuel card issue for vehicle HL-22 — need approval to re-issue",
                            body="Portal request raised. Needs your approval.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/fleet/fuelcards/requests/HL-22"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Relations",
                            sender_email=f"carriers@{dom}",
                            subject="Carrier missed slot — reschedule in portal",
                            body="Please reschedule the missed slot in the carrier portal to avoid penalties.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[
                                f"https://{dom}/logistics/carriers/slots/reschedule?ref=SL-1881"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Broker (NorthGate)",
                            sender_email="ops@northgatebrokerage.co.uk",
                            subject="Customs hold: additional commodity description needed",
                            body="Hi,\n\nCustoms need additional commodity description on shipment HL-7741.\n\nThanks,\nNorthGate",
                            is_phish=False,
                            difficulty=4,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="Shipment HL-7741 — upload broker response (portal)",
                            body="Upload broker response and supporting docs in the customs portal.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/customs/shipments/HL-7741"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Accounts Payable",
                            sender_email=f"accounts@{dom}",
                            subject="Invoice received: CARR-99118 (PDF attached)",
                            body="Carrier invoice attached.",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["CARR-99118.pdf"],
                        ),
                        e(
                            sender_name="Procurement System",
                            sender_email=f"no-reply@{dom}",
                            subject="Vendor bank change request logged — verification required (portal)",
                            body="A vendor bank change requires verification steps before approval.",
                            is_phish=False,
                            difficulty=4,
                            category="procurement",
                            links=[f"{vendor_portal}/bank-changes/verify?case=BC-4402"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Aisha Khan",
                            sender_email=f"aisha.khan@{dom}",
                            subject="Clip from loading bay cam — might help with the missed slot",
                            body=(
                                "I pulled a clip showing the carrier arriving late.\n"
                                f"Uploaded internally here:\n{docs_portal}/shared/clip?id=SL-1881\n"
                            ),
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"{docs_portal}/shared/clip?id=SL-1881"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Portal",
                            sender_email=f"no-reply@{slug}-tracking.com",
                            subject="Delivery slot penalty notice — confirm reschedule",
                            body=f"Confirm new slot:\nhttp://{slug}-tracking.com/reschedule/SL-1881\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{slug}-tracking.com/reschedule/SL-1881"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Invoice",
                            sender_email=f"customs@{docs_spoof}",
                            subject="Customs fee invoice attached — pay to release shipment HL-7741",
                            body="Invoice attached. Pay to release shipment.",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[],
                            attachments=["CustomsFee_HL-7741.pdf.scr"],
                        ),
                        e(
                            sender_name="Banking Alerts",
                            sender_email=f"alerts@{bank_spoof}",
                            subject="Unusual payment run flagged — verify beneficiary now",
                            body=f"Verify beneficiary:\nhttp://{bank_spoof}/verify/beneficiary\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{bank_spoof}/verify/beneficiary"],
                            attachments=[],
                        ),
                        e(
                            sender_name=scenario.line_manager_name,
                            sender_email=mgr_email,
                            subject="Keep an audit trail today — multiple escalations expected",
                            body="Log decisions + rationale as you go. Escalate anything weird before acting.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/portal/notes/depot-ops"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities",
                            sender_email=f"facilities@{dom}",
                            subject="Forklift maintenance window — acknowledge schedule",
                            body="Please acknowledge schedule so we can plan loading bay access.",
                            is_phish=False,
                            difficulty=4,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/maintenance/forklift?week=current"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Service Desk",
                            sender_email=f"support@{dom}",
                            subject="Depot Wi-Fi upgrade tonight — confirm critical devices list (portal)",
                            body="Confirm list of devices requiring uninterrupted connectivity.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"{it_portal}/changes/wifi-upgrade/depot"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Wi-Fi Team",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="Device list needed — upload via secure form",
                            body=f"Upload:\nhttp://{helpdesk_spoof}/forms/device-list\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/forms/device-list"],
                            attachments=[],
                        ),
                        e(
                            sender_name="VendorHub",
                            sender_email=f"no-reply@{vendorhub_spoof}",
                            subject="Bank change verification failed — re-enter details",
                            body=f"Re-enter:\nhttp://{vendorhub_spoof}/bank/re-enter?case=BC-4402\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{vendorhub_spoof}/bank/re-enter?case=BC-4402"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Agency Staffing",
                            sender_email="ops@fastcoverstaffing.co.uk",
                            subject="Re: agency cover request — rates attached",
                            body="Hi,\n\nRates attached. Please confirm if you want 2 drivers for AM.\n\nThanks",
                            is_phish=False,
                            difficulty=4,
                            category="external",
                            links=[],
                            attachments=["Agency_Rates_AM.pdf"],
                        ),
                        e(
                            sender_name="Finance Ops",
                            sender_email=f"finance-ops@{dom}",
                            subject="Payment run note: bank changes must be verified (policy PDF)",
                            body="Reminder attached.",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["Bank_Change_Policy.pdf"],
                        ),
                        e(
                            sender_name="NorthGate Brokerage",
                            sender_email="ops@northgatebrokerage.co.uk",
                            subject="RE: HL-7741 — details received, submitting to customs now",
                            body="Thanks — we’ve submitted the update. Will advise once released.",
                            is_phish=False,
                            difficulty=4,
                            category="external",
                            links=[],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Relations",
                            sender_email=f"carriers@{dom}",
                            subject="Penalty risk: slot not rescheduled by 14:00",
                            body="Please reschedule the slot in the portal to avoid auto-penalty.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[
                                f"https://{dom}/logistics/carriers/slots/reschedule?ref=SL-1881&urgent=1"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Shared Document",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Shared file: Depot_Schedule_Changes.xlsm",
                            body=f"Open:\nhttp://{docs_spoof}/open?id=depot-schedule\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/open?id=depot-schedule"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="Broker response uploaded — please approve submission (portal)",
                            body="Approve submission so the case can proceed.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/customs/shipments/HL-7741/approve"],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Customs Desk",
                            sender_email=f"customs@{dom}",
                            subject="Wave: customs release window today — final approval needed",
                            body="If we miss the window, shipment moves to tomorrow.",
                            is_phish=False,
                            difficulty=5,
                            category="internal",
                            links=[
                                f"https://{dom}/customs/shipments/HL-7741/approve?window=today"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Carrier Portal",
                            sender_email=f"no-reply@{slug}-tracking.com",
                            subject="Wave: slot cancelled — confirm within 30 mins",
                            body=f"Confirm:\nhttp://{slug}-tracking.com/confirm/cancelled\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{slug}-tracking.com/confirm/cancelled"],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Wave: absence records incomplete — please finalise today",
                            body="Please finalise absence records and note cover arrangements.",
                            is_phish=False,
                            difficulty=5,
                            category="hr",
                            links=[
                                f"{hr_portal}/absence/cases?dept=depot-ops&status=open"
                            ],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        if level_no == 14:
            defs.append(
                dict(
                    scenario=scenario,
                    number=14,
                    title="Event week chaos: rooms + guests + HR liaison + finance compliance",
                    briefing=(
                        "Room moves, guest access, suppliers, travel, and pay queries collide. "
                        "Phish will look like university portals and shared docs."
                    ),
                    scenario_overrides=level_overrides.get(14, {}),
                    base_emails=[
                        e(
                            sender_name="Timetabling",
                            sender_email=f"timetabling@{dom}",
                            subject="Room change: Monday lecture moved (portal)",
                            body="Room change posted. Please notify affected staff.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[
                                f"https://{dom}/portal/timetabling/changes?week=current"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Events Team",
                            sender_email=f"events@{dom}",
                            subject="Guest speaker access list due today (portal upload)",
                            body="Please upload names for guest passes by 16:00.",
                            is_phish=False,
                            difficulty=4,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/events/guest-passes/upload?event=EV-992"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Delivery expected: staging + AV equipment — confirm loading bay slot",
                            body="Confirm loading bay slot and contact for handover.",
                            is_phish=False,
                            difficulty=4,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/deliveries/confirm?ref=EV-AV-210"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Shared Services",
                            sender_email=f"hr@{dom}",
                            subject="Pay query routing reminder (portal)",
                            body="Pay queries must be logged in HR portal with reference details.",
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[f"{hr_portal}/pay/help"],
                            attachments=[],
                        ),
                        e(
                            sender_name="School Finance",
                            sender_email=f"school-finance@{dom}",
                            subject="Travel claim submitted — receipt summary attached",
                            body="Receipt summary attached for your records.",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["Travel_Claim_Summary.pdf"],
                        ),
                        e(
                            sender_name="Research Office",
                            sender_email=f"research-office@{dom}",
                            subject="Research account compliance check — respond in portal",
                            body="Please respond to compliance questions in the portal.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/research/compliance/checks/RC-1881"],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Status",
                            sender_email=f"it-status@{dom}",
                            subject="Notice: portal maintenance tonight (status)",
                            body="Scheduled maintenance 22:00–23:30.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"{it_portal}/status/maintenance"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Colleague (Sam)",
                            sender_email=f"sam.walters@{dom}",
                            subject="Clip from last year’s event — for the promo slide?",
                            body=f"Internal clip link:\n{docs_portal}/shared/clip?id=promo-2019\n",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"{docs_portal}/shared/clip?id=promo-2019"],
                            attachments=[],
                        ),
                        e(
                            sender_name="University SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Shared: Guest_Access_List_EV-992.xlsx (open)",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=EV-992-guestlist\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{sharepoint_spoof}/open?id=EV-992-guestlist"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="HR Portal",
                            sender_email=f"no-reply@{payroll_spoof}",
                            subject="Payroll adjustment notice — confirm to avoid delay",
                            body=f"Confirm:\nhttp://{payroll_spoof}/confirm/adjustment\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{payroll_spoof}/confirm/adjustment"],
                            attachments=[],
                        ),
                        e(
                            sender_name="AV Supplier",
                            sender_email=f"billing@{vendorhub_spoof}",
                            subject="Deposit required to release AV delivery today",
                            body=f"Pay deposit:\nhttp://{vendorhub_spoof}/pay/deposit?ref=EV-AV-210\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{vendorhub_spoof}/pay/deposit?ref=EV-AV-210"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="Secure Document",
                            sender_email=f"no-reply@{docs_spoof}",
                            subject="Document shared: Event_Room_Changes.docm",
                            body=f"Download:\nhttp://{docs_spoof}/download?id=room-changes\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{docs_spoof}/download?id=room-changes"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Events Team",
                            sender_email=f"events@{dom}",
                            subject="Catering numbers needed by 15:00",
                            body="Please confirm attendee count estimate so catering can finalise.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/events/EV-992/catering"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Facilities Desk",
                            sender_email=f"facilities@{dom}",
                            subject="Fire marshal note: max occupancy reminder for updated room",
                            body="Reminder: confirm occupancy limits for the new room assignment.",
                            is_phish=False,
                            difficulty=4,
                            category="facilities",
                            links=[f"{facilities_portal}/rooms/occupancy?room=H3.12"],
                            attachments=[],
                        ),
                        e(
                            sender_name="School HR Liaison",
                            sender_email=f"hr-liaison@{dom}",
                            subject="Sickness policy reminder (PDF attached)",
                            body="Policy attached for quick reference.",
                            is_phish=False,
                            difficulty=4,
                            category="hr",
                            links=[],
                            attachments=["Sickness_Policy_QuickRef.pdf"],
                        ),
                        e(
                            sender_name="School Finance",
                            sender_email=f"school-finance@{dom}",
                            subject="Supplier invoice received: AV-5518 (PDF attached)",
                            body="Invoice attached. Please confirm cost centre for event.",
                            is_phish=False,
                            difficulty=4,
                            category="finance",
                            links=[],
                            attachments=["AV-5518.pdf"],
                        ),
                        e(
                            sender_name="Research Office",
                            sender_email=f"research-office@{dom}",
                            subject="Reminder: compliance responses due today",
                            body="Please respond in portal; follow-up required for closure.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[
                                f"https://{dom}/research/compliance/checks/RC-1881?due=today"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="IT Service Desk",
                            sender_email=f"support@{dom}",
                            subject="Event account access: temporary guest Wi-Fi codes (portal)",
                            body="Codes available in portal; do not share externally.",
                            is_phish=False,
                            difficulty=4,
                            category="it",
                            links=[f"{it_portal}/wifi/guest-codes?event=EV-992"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Guest Services",
                            sender_email=f"guestservices@{dom}",
                            subject="VIP guest arrival times — confirm schedule",
                            body="Please confirm arrival schedule so security can prepare.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[f"https://{dom}/events/EV-992/vip-schedule"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Guest Services",
                            sender_email=f"no-reply@{helpdesk_spoof}",
                            subject="VIP schedule requires verification (secure link)",
                            body=f"Verify:\nhttp://{helpdesk_spoof}/vip/verify\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[f"http://{helpdesk_spoof}/vip/verify"],
                            attachments=[],
                        ),
                        e(
                            sender_name="Timetabling",
                            sender_email=f"timetabling@{dom}",
                            subject="Reminder: notify staff of room changes",
                            body="Please notify staff today; signage will be updated tomorrow.",
                            is_phish=False,
                            difficulty=4,
                            category="internal",
                            links=[],
                            attachments=[],
                        ),
                    ],
                    wave_emails=[
                        e(
                            sender_name="Events Team",
                            sender_email=f"events@{dom}",
                            subject="Wave: guest list incomplete — security needs it within 1 hour",
                            body="Please upload the final list ASAP.",
                            is_phish=False,
                            difficulty=5,
                            category="facilities",
                            links=[
                                f"{facilities_portal}/events/guest-passes/upload?event=EV-992&urgent=1"
                            ],
                            attachments=[],
                        ),
                        e(
                            sender_name="University SharePoint",
                            sender_email=f"no-reply@{sharepoint_spoof}",
                            subject="Wave: Updated_Guest_List_EV-992.xlsx (open)",
                            body=f"Open:\nhttp://{sharepoint_spoof}/open?id=EV-992-guestlist-v2\n",
                            is_phish=True,
                            difficulty=5,
                            category="phish",
                            links=[
                                f"http://{sharepoint_spoof}/open?id=EV-992-guestlist-v2"
                            ],
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
                            links=[f"{it_portal}/status/maintenance?update=1"],
                            attachments=[],
                        ),
                    ],
                )
            )
            continue

        defs.append(
            dict(
                scenario=scenario,
                number=15,
                title="Peak operational overload: payroll + banking + supplier fraud amid incidents",
                briefing=(
                    "Highest load so far. You’re deep in org reality: people issues, facilities, supplier pressure, "
                    "banking verification, and IT instability overlap. Phish is contextual, polished, and urgent."
                ),
                scenario_overrides=level_overrides.get(15, {}),
                base_emails=[
                    e(
                        sender_name="IT Status",
                        sender_email=f"it-status@{dom}",
                        subject="Incident: intermittent SSO failures (status)",
                        body="SSO intermittent. Track updates on status page.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"{it_portal}/status/sso-incident"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Security Operations",
                        sender_email=f"soc@{dom}",
                        subject="Security advisory: attackers exploiting incident comms",
                        body="Do not follow authentication links from email. Use the internal portal.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[
                            f"https://{dom}/security/advisories/incident-exploitation"
                        ],
                        attachments=[],
                    ),
                    e(
                        sender_name="Facilities Desk",
                        sender_email=f"facilities@{dom}",
                        subject="Delivery expected: replacement desks — confirm bay slot (today)",
                        body="Confirm bay slot and escort contact.",
                        is_phish=False,
                        difficulty=5,
                        category="facilities",
                        links=[f"{facilities_portal}/deliveries/confirm?ref=DESK-8811"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Site Security",
                        sender_email=f"security@{dom}",
                        subject="Visitor list needed for DESK-8811 delivery",
                        body="Upload visitor list + vehicle regs. Do not email personal data externally.",
                        is_phish=False,
                        difficulty=5,
                        category="security",
                        links=[f"{facilities_portal}/visitors/upload?ref=DESK-8811"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Sana Ahmed",
                        sender_email=f"sana.ahmed@{dom}",
                        subject="I need to take tomorrow off — family emergency (what’s the process?)",
                        body="Can you advise process and whether I should log it anywhere?",
                        is_phish=False,
                        difficulty=5,
                        category="hr",
                        links=[],
                        attachments=[],
                    ),
                    e(
                        sender_name="HR Shared Services",
                        sender_email=f"hr@{dom}",
                        subject="Manager action: leave request awaiting approval (portal)",
                        body="Please approve/decline in the portal.",
                        is_phish=False,
                        difficulty=5,
                        category="hr",
                        links=[f"{hr_portal}/leave/approvals?team=ops-finance"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Payroll Team",
                        sender_email=f"payroll@{dom}",
                        subject="Payroll run confirmation — managers to review exception list (portal)",
                        body="Review exception list and flag anomalies by 16:00.",
                        is_phish=False,
                        difficulty=5,
                        category="hr",
                        links=[f"{hr_portal}/payroll/exceptions?run=monthly"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Accounts Payable",
                        sender_email=f"accounts@{dom}",
                        subject="Invoice received: INV-24190 (PDF attached)",
                        body="Invoice attached. Please confirm match / exception handling.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[],
                        attachments=["INV-24190.pdf"],
                    ),
                    e(
                        sender_name="Procurement System",
                        sender_email=f"no-reply@{dom}",
                        subject="Vendor bank change request: BC-8820 (verification required)",
                        body="Verification required before approval.",
                        is_phish=False,
                        difficulty=5,
                        category="procurement",
                        links=[f"{vendor_portal}/bank-changes/verify?case=BC-8820"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Westridge Supplies",
                        sender_email="billing@westridgesupplies.co.uk",
                        subject="URGENT: remittance failed — confirm updated account for today’s run",
                        body=(
                            "Hello,\n\nOur remittance failed. Please confirm the updated account is used today.\n"
                            "If you need a letterhead confirmation we can provide.\n\nBilling"
                        ),
                        is_phish=False,
                        difficulty=5,
                        category="supplier",
                        links=[],
                        attachments=[],
                    ),
                    e(
                        sender_name="Finance Controls",
                        sender_email=f"controls@{dom}",
                        subject="Reminder: bank change verification steps (PDF attached)",
                        body="Reminder attached. No exceptions during incident periods.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[],
                        attachments=["BankChange_Verification_Steps.pdf"],
                    ),
                    e(
                        sender_name="Parcel Delivery",
                        sender_email="no-reply@parceltrack-mail.com",
                        subject="Your personal parcel is arriving today — choose a safe place",
                        body="Choose safe place:\nhttps://parceltrack-mail.com/options\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=["https://parceltrack-mail.com/options"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Payroll Exceptions",
                        sender_email=f"no-reply@{payroll_spoof}",
                        subject="Payroll exception requires manager verification (today)",
                        body=f"Verify exception:\nhttp://{payroll_spoof}/exceptions/verify\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{payroll_spoof}/exceptions/verify"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Finance Approvals",
                        sender_email=f"no-reply@{finance_spoof}",
                        subject="Payment run blocked — approve vendor update BC-8820 now",
                        body=f"Approve:\nhttp://{finance_spoof}/approve?case=BC-8820\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{finance_spoof}/approve?case=BC-8820"],
                        attachments=[],
                    ),
                    e(
                        sender_name=f"{scenario.company_name} SharePoint",
                        sender_email=f"no-reply@{sharepoint_spoof}",
                        subject="Shared: BankChange_Confirmation_BC-8820.pdf (open)",
                        body=f"Open:\nhttp://{sharepoint_spoof}/open?id=BC-8820-confirm\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{sharepoint_spoof}/open?id=BC-8820-confirm"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Banking Alerts",
                        sender_email=f"alerts@{bank_spoof}",
                        subject="Beneficiary flagged — re-authenticate to release payment",
                        body=f"Re-auth:\nhttp://{bank_spoof}/reauth/release\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{bank_spoof}/reauth/release"],
                        attachments=[],
                    ),
                    e(
                        sender_name="IT SSO Team",
                        sender_email=f"no-reply@{helpdesk_spoof}",
                        subject="SSO fix requires immediate re-login",
                        body=f"Re-login:\nhttp://{helpdesk_spoof}/sso/relogin\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{helpdesk_spoof}/sso/relogin"],
                        attachments=[],
                    ),
                    e(
                        sender_name=scenario.line_manager_name,
                        sender_email=mgr_email,
                        subject="Keep coverage stable — approve leave quickly but document",
                        body="Approve/decline quickly, but add notes for audit trail. Escalate anything odd.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[f"https://{dom}/portal/notes/ops-finance?day=today"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Internal Audit",
                        sender_email=f"audit@{dom}",
                        subject="Audit sample request: bank change evidence (upload)",
                        body="Upload evidence for recent bank change approvals. Deadline EOD.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[
                            f"{finance_portal}/audit/evidence/upload?topic=bank-changes"
                        ],
                        attachments=[],
                    ),
                    e(
                        sender_name="Service Desk",
                        sender_email=f"support@{dom}",
                        subject="Ticket: user locked out during SSO incident (portal)",
                        body="Please update ticket with your status/notes.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"{it_portal}/servicedesk/tickets/SD-25102"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Facilities Desk",
                        sender_email=f"facilities@{dom}",
                        subject="Reminder: escort needed for DESK-8811 at 12:10",
                        body="Please confirm escort in portal.",
                        is_phish=False,
                        difficulty=5,
                        category="facilities",
                        links=[
                            f"{facilities_portal}/deliveries/confirm?ref=DESK-8811&reminder=1"
                        ],
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
                        links=[f"{vendor_portal}/changes/pending?case=VND-5520"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Legal Ops",
                        sender_email=f"legal@{dom}",
                        subject="Reminder: do not approve financial changes based on email requests",
                        body="Use approved verification channels and record evidence.",
                        is_phish=False,
                        difficulty=5,
                        category="legal",
                        links=[f"https://{dom}/legal/policy/verification"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Secure Document",
                        sender_email=f"no-reply@{docs_spoof}",
                        subject="Document shared: Audit_Evidence_Request.docm",
                        body=f"Download:\nhttp://{docs_spoof}/download?id=audit-evidence\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{docs_spoof}/download?id=audit-evidence"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Colleague (Jordan Reeves)",
                        sender_email=f"jordan.reeves@{dom}",
                        subject="FYI: vendor calling nonstop asking if they’re on today’s run",
                        body="They’re pushing hard. I haven’t confirmed anything — just letting you know.",
                        is_phish=False,
                        difficulty=5,
                        category="internal",
                        links=[],
                        attachments=[],
                    ),
                    e(
                        sender_name="Finance Ops",
                        sender_email=f"finance-ops@{dom}",
                        subject="Payment run: approvals reopen due to incident delays (portal)",
                        body="Approvals reopened. Please re-check queue.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[f"{finance_portal}/payments/approvals?reopen=1"],
                        attachments=[],
                    ),
                ],
                wave_emails=[
                    e(
                        sender_name="Finance Ops",
                        sender_email=f"finance-ops@{dom}",
                        subject="Wave: payment run cut-off moved earlier (15:30)",
                        body="Due to incident, cut-off moved. Please finalise approvals early.",
                        is_phish=False,
                        difficulty=5,
                        category="finance",
                        links=[f"{finance_portal}/payments/approvals?cutoff=1530"],
                        attachments=[],
                    ),
                    e(
                        sender_name="Banking Alerts",
                        sender_email=f"alerts@{bank_spoof}",
                        subject="Wave: last chance — beneficiary verification pending",
                        body=f"Verify:\nhttp://{bank_spoof}/verify/beneficiary?last=1\n",
                        is_phish=True,
                        difficulty=5,
                        category="phish",
                        links=[f"http://{bank_spoof}/verify/beneficiary?last=1"],
                        attachments=[],
                    ),
                    e(
                        sender_name="IT Status",
                        sender_email=f"it-status@{dom}",
                        subject="Wave: SSO incident stabilising (status)",
                        body="SSO stabilising. See status page for steps.",
                        is_phish=False,
                        difficulty=5,
                        category="it",
                        links=[f"{it_portal}/status/sso-incident?update=stabilising"],
                        attachments=[],
                    ),
                ],
            )
        )

    return defs
