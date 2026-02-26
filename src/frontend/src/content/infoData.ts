// src/frontend/src/content/infoData.ts

export type InfoRule = {
  id: string; // e.g. "links.mismatch"
  title: string; // short heading
  summary: string; // 1–2 lines
  details: string[]; // bullet points
  examples?: string[]; // optional examples
  tags: string[]; // for filtering later (hints/metrics)
};

export type InfoSection = {
  id: string; // e.g. "basics"
  title: string;
  intro: string;
  rules: InfoRule[];
};

export const infoSections: InfoSection[] = [
  {
    id: 'about',
    title: 'About this application',
    intro:
      'This platform trains phishing detection using realistic emails and timed decision-making. The goal is to build habits you can use in the real world: slow down, verify, and act safely.',
    rules: [
      {
        id: 'about.core-loop',
        title: 'The core loop (all modes)',
        summary:
          'Read the email, check the clues, decide how you would respond, then learn from the outcome.',
        details: [
          'Start by scanning the sender, subject, and overall tone.',
          'Read the body carefully and look for “pressure” tactics (urgency, fear, reward).',
          'Inspect links and attachments before acting.',
          'Decide: report as phishing or treat as safe/normal.',
          'Use feedback to build pattern recognition (without relying on “gotcha” answers).',
        ],
        tags: ['gameplay'],
      },
      {
        id: 'about.arcade',
        title: 'Arcade mode',
        summary: 'Quick-fire practice. You build speed and baseline instincts.',
        details: [
          'You see one email at a time and make a fast decision.',
          'It is ideal for beginners and warm-ups.',
          'Focus on spotting common red flags quickly (sender oddities, suspicious links, pressure language).',
        ],
        tags: ['gameplay', 'arcade'],
      },
      {
        id: 'about.simulator',
        title: 'Inbox simulator',
        summary:
          'Scenario-based levels with workplace context. You build judgement, not just reflexes.',
        details: [
          'You play inside an inbox-like interface.',
          'Some actions are gated (e.g. opening a link/attachment before marking read) to train safe habits.',
          'Context matters: which emails make sense for your role, department, and current tasks?',
          'Higher levels may include “waves” (late-arriving emails) designed to add pressure.',
        ],
        tags: ['gameplay', 'simulator'],
      },
      {
        id: 'about.pvp',
        title: 'PVP (player-made levels)',
        summary:
          'Create challenge levels and play others. This trains attacker-thinking and deeper analysis.',
        details: [
          'When creating levels, you learn what attackers try to exploit.',
          'When playing, you encounter more varied styles and trickier social engineering.',
          'Good creators design fair challenges: realistic content with subtle signals.',
        ],
        tags: ['gameplay', 'pvp'],
      },
    ],
  },

  {
    id: 'what-is-phish',
    title: 'What is phishing?',
    intro:
      'Phishing is a type of social engineering where an attacker tries to trick you into doing something unsafe - usually by pretending to be a trusted person or organisation.',
    rules: [
      {
        id: 'phish.definition',
        title: 'The goal of a phish',
        summary:
          'To steal information, money, access, or to get you to run something malicious.',
        details: [
          'Credential theft (passwords, MFA codes, login sessions).',
          'Financial fraud (invoice scams, gift cards, payment diversion).',
          'Malware delivery (attachments, drive-by downloads, fake updates).',
          'Account takeover (reset links, “verify your account” prompts).',
        ],
        tags: ['basics', 'phishing', 'arcade-hint'],
      },
      {
        id: 'phish.social-engineering',
        title: 'Why phishing works',
        summary:
          'It targets human behaviour: urgency, trust, fear of consequences, and helpfulness.',
        details: [
          'Attackers often pick believable pretexts (IT support, HR, deliveries, invoices).',
          'They add time pressure to reduce careful checking.',
          'They rely on you “doing the normal thing” (clicking, replying, opening attachments).',
        ],
        tags: ['basics', 'psychology', 'arcade-hint'],
      },
      {
        id: 'phish.not-just-email',
        title: 'It is not just email',
        summary:
          'The same techniques appear in texts, phone calls, messaging apps, and social media. "scam calls" are actually forms of phishing.',
        details: [
          'Smishing: phishing via SMS/text.',
          'Vishing: phishing via voice calls.',
          'Impersonation via chat tools (Teams/Slack/Discord).',
          'Social media messages that lure you to a login page or “support” account.',
        ],
        tags: ['basics'],
      },
    ],
  },

  {
    id: 'basic-techniques',
    title: 'Basic detection techniques',
    intro:
      'These are the fundamentals: quick checks that catch a large percentage of common phishing attempts. Perfect for Arcade mode.',
    rules: [
      {
        id: 'basic.sender',
        title: 'Check the sender carefully',
        summary:
          'Look for mismatched names and domains, odd formatting, and small spelling changes.',
        details: [
          'A display name can be faked; the email address is more important.',
          'Watch for lookalike domains (e.g. “micros0ft”, extra hyphens, swapped letters).',
          'Be suspicious if the sender does not match the organisation they claim to represent.',
        ],
        examples: [
          '“IT Support <support@it-helpdesk.example>” asking for your Microsoft password.',
        ],
        tags: ['basics', 'sender', 'arcade-hint'],
      },
      {
        id: 'basic.urgency',
        title: 'Spot urgency and pressure',
        summary: '“Act now” language is often used to override your judgement.',
        details: [
          'Threats: “account will be closed”, “final warning”, “disciplinary action”.',
          'Rewards: “you’ve won”, “refund available”, “bonus approved”.',
          'Time traps: “in the next 30 minutes”, “today only”.',
        ],
        tags: ['basics', 'psychology', 'arcade-hint'],
      },
      {
        id: 'basic.links',
        title: 'Treat links as untrusted by default',
        summary: 'A normal-looking link can still be dangerous.',
        details: [
          'Check the domain and the full address, not just the text.',
          'Shortened links hide the destination.',
          'Be wary of login pages reached from emails - prefer navigating yourself.',
        ],
        tags: ['basics', 'links', 'arcade-hint'],
      },
      {
        id: 'basic.attachments',
        title: 'Be cautious with attachments',
        summary: 'Attachments are a common malware route, especially if unexpected.',
        details: [
          'Ask: were you expecting this file from this person?',
          'Watch for double extensions (e.g. “invoice.pdf.exe”).',
          'Be cautious with macro-enabled documents or requests to “enable editing/content”.',
        ],
        tags: ['basics', 'attachments', 'arcade-hint'],
      },
      {
        id: 'basic.language',
        title: 'Watch the writing quality and tone',
        summary:
          'Phishing often contains awkward phrasing, unusual tone, or generic greetings.',
        details: [
          'Generic greetings: “Dear user”, “Hello customer”.',
          'Inconsistent tone: too formal, too pushy, or oddly casual for the sender.',
          'Errors are a clue, but not proof - advanced attackers can write well.',
        ],
        tags: ['basics', 'content', 'arcade-hint'],
      },
    ],
  },

  {
    id: 'intermediate-techniques',
    title: 'Intermediate detection techniques',
    intro:
      'These checks help when emails are more realistic and context-driven (Inbox simulator levels). They focus on verification and consistency.',
    rules: [
      {
        id: 'intermediate.consistency',
        title: 'Check for consistency across the email',
        summary:
          'Real internal emails tend to be consistent about names, roles, processes, and terminology.',
        details: [
          'Does the request match normal workplace processes?',
          'Is the signature consistent with the sender’s claimed role?',
          'Do the details line up (dates, reference numbers, project names, teams)?',
        ],
        tags: ['intermediate', 'context', 'sim-hint'],
      },
      {
        id: 'intermediate.reply-chain',
        title: 'Be wary of “reply chain” tricks',
        summary: 'Attackers sometimes fake conversation history to look legitimate.',
        details: [
          'Quoted text can be fabricated.',
          'Look for mismatched subject lines vs the supposed conversation.',
          'IRL - If in doubt, verify via a known channel (phone, internal chat, direct navigation).',
        ],
        tags: ['intermediate', 'spoofing', 'sim-hint'],
      },
      {
        id: 'intermediate.login-path',
        title: 'Prefer safe navigation over emailed login links',
        summary:
          'If you must log in, navigate to the service yourself rather than clicking a link.',
        details: [
          'Use bookmarks or type the known domain yourself.',
          'If the email claims “your session expired”, open a new tab and log in normally.',
          'Treat MFA prompts as suspicious if you did not initiate a login.',
        ],
        tags: ['intermediate', 'links', 'account', 'sim-hint'],
      },
      {
        id: 'intermediate.secondary-channel',
        title: 'IRL- Verify using a second channel',
        summary:
          'A quick independent check stops many high-quality social engineering attempts.',
        details: [
          'If it is “Finance”, message Finance using the usual internal contact.',
          'If it is “IT”, open the IT portal you already know or call the helpdesk number you trust.',
          'If it is a supplier, use the phone number on record - not the one in the email.',
        ],
        tags: ['intermediate', 'verification', 'sim-hint'],
      },
      {
        id: 'intermediate.workflow',
        title: 'Think about workplace context',
        summary: 'Ask: “Would I realistically receive this email in this role, today?”',
        details: [
          'Does it match your department’s responsibilities?',
          'Is the timing plausible (e.g. “urgent invoice” on a Sunday night)?',
          'Is the requested action normal (gift cards, personal email replies, secrecy)?',
        ],
        tags: ['intermediate', 'context', 'sim-hint'],
      },
    ],
  },

  {
    id: 'advanced-techniques',
    title: 'Advanced detection techniques',
    intro:
      'These apply when emails are long, detailed, and designed to defeat simple red-flag checking. Here you focus on subtle signals and rigorous verification.',
    rules: [
      {
        id: 'advanced.bec',
        title: 'Business Email Compromise (BEC) patterns',
        summary:
          'High-impact scams that look plausible and target payments or sensitive data.',
        details: [
          'Payment diversion: “new bank details”, “use this account urgently”.',
          'CEO fraud: “I need this done discreetly right now”.',
          'Supplier impersonation: invoice changes, updated payment details, or “overdue” pressure.',
          'The language may be clean and professional - rely on process verification, not grammar.',
        ],
        tags: ['advanced', 'finance', 'impersonation', 'sim-hint'],
      },
      {
        id: 'advanced.subtle-links',
        title: 'Subtle link deception',
        summary:
          'Links can be crafted to look correct at a glance but resolve somewhere else.',
        details: [
          'Look for extra subdomains (e.g. “login.company.com.attacker-site.example”).',
          'Watch for punycode/Unicode tricks (characters that look like Latin letters).',
          'Be wary of “file share” links that lead to login pages.',
        ],
        tags: ['advanced', 'links'],
      },
      {
        id: 'advanced.long-email',
        title: 'Long emails and “over-explaining”',
        summary:
          'Attackers sometimes use lots of detail to create credibility and reduce suspicion.',
        details: [
          'Long context does not equal legitimacy.',
          'Spot the key request: what do they actually want you to do?',
          'If the action is risky (credentials, money, installs), verify out-of-band.',
        ],
        tags: ['advanced', 'content'],
      },
      {
        id: 'advanced.mfa-fatigue',
        title: 'MFA fatigue and session tricks',
        summary:
          'Repeated prompts or “session expired” messages try to get you to approve access.',
        details: [
          'Do not approve MFA prompts you did not initiate.',
          'Repeated prompts can indicate someone has your password.',
          'Report unusual login alerts and change credentials via trusted navigation.',
        ],
        tags: ['advanced', 'account'],
      },
      {
        id: 'advanced.process',
        title: 'Rely on process, not gut feel',
        summary:
          'The best defence is predictable verification steps, even when you are busy.',
        details: [
          'Use known contacts and known systems.',
          'Follow approval steps for payments and sensitive changes.',
          'If something is “urgent”, that is exactly when you should slow down.',
        ],
        tags: ['advanced', 'verification', 'context', 'sim-hint'],
      },
    ],
  },

  {
    id: 'becoming-adversary',
    title: 'Becoming the adversary (attacker mindset)',
    intro:
      'PVP mode is where you learn to think like an attacker. This does not teach wrongdoing - it teaches how deception is shaped so you can recognise it.',
    rules: [
      {
        id: 'adversary.pretext',
        title: 'A strong pretext beats obvious red flags',
        summary:
          'Attackers start with a believable story that fits the victim’s context.',
        details: [
          'They pick roles with authority (IT, HR, Finance, a manager).',
          'They pick moments of distraction (deadlines, end of day, policy changes).',
          'They mirror workplace language and processes where possible.',
        ],
        tags: ['adversary', 'context', 'psychology'],
      },
      {
        id: 'adversary.pressure',
        title: 'Pressure is the tool',
        summary: 'The email’s goal is usually to reduce your checking behaviour.',
        details: [
          'Urgency, fear, reward, curiosity, or “confidentiality”.',
          'Small requests first (“quick check”) then bigger ones (credentials/payment).',
          'Polite tone can be as manipulative as aggressive tone.',
        ],
        tags: ['adversary', 'psychology'],
      },
      {
        id: 'adversary.fair-design',
        title: 'Design fair challenges (PVP creators)',
        summary:
          'Good PVP levels are realistic and teach something - not random nonsense.',
        details: [
          'Make the email plausible for the scenario, role, and department.',
          'Include subtle but detectable clues (domain mismatch, process deviation, suspicious link path).',
          'Avoid impossible puzzles; the player should learn a real-world lesson.',
        ],
        tags: ['adversary', 'pvp'],
      },
      {
        id: 'adversary.defender-habit',
        title: 'Defender habit: “Verify before you comply”',
        summary:
          'If you can predict what the attacker wants, you can block it with verification.',
        details: [
          'Credentials? Navigate yourself and confirm the domain.',
          'Money? Verify payment changes using known contacts and approvals.',
          'Attachments? Confirm expectation and legitimacy before opening.',
        ],
        tags: ['adversary', 'verification'],
      },
    ],
  },
];
