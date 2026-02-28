import { Email } from '../api';

const URGENCY_RE =
  /\b(urgent|immediately|verify now|action required|final warning|account locked|within 24 hours|avoid restriction|suspended|overdue|asap|today only)\b/i;

const GENERIC_GREETING_RE =
  /\b(dear (customer|user|client)|hello customer|dear colleague)\b/i;

const MFA_RE =
  /\b(mfa|multi[- ]factor|one[- ]time code|otp|push notification|authenticator)\b/i;

const CRED_RE =
  /\b(password|passcode|sign in|login|verify your account|reset your password)\b/i;

const REPLY_CHAIN_RE =
  /\b(-----original message-----|from:\s.*\n|sent:\s.*\n|to:\s.*\n|subject:\s.*\n)\b/i;

const PAYMENT_RE =
  /\b(bank details|sort code|account number|payment|transfer|wire|invoice|remittance|purchase order|gift card)\b/i;

const RISKY_EXT_RE =
  /\.(exe|js|bat|cmd|scr|msi|ps1|vbs|jar|docm|xlsm|pptm|zip|rar)\b/i;

function domainOfEmail(addr: string): string {
  const a = (addr || '').trim().toLowerCase();
  const at = a.indexOf('@');
  if (at === -1) return '';
  return a.slice(at + 1);
}

function hostnameOfUrl(u: string): string {
  try {
    return new URL((u || '').trim()).hostname.toLowerCase();
  } catch {
    return '';
  }
}

function rootDomain(d: string): string {
  const s = (d || '').trim().toLowerCase();
  if (!s) return '';
  const parts = s.split('.');
  if (parts.length < 2) return s;
  return parts.slice(-2).join('.');
}

/**
 * Rules that are good educational content but NOT actionable inside our game UI,
 * so we never surface them as hints.
 */
const DISALLOWED_HINT_RULE_IDS = new Set<string>([
  'about.core-loop',
  'about.arcade',
  'about.simulator',
  'about.pvp',
  'phish.definition',
  'phish.social-engineering',
  'phish.not-just-email',
  // user called these out:
  'intermediate.login-path',
  'intermediate.secondary-channel',
  'adversary.defender-habit',
]);

/**
 * For SIMULATION mode only:
 * Return up to 4 hint rule IDs to show in the end-of-level modal.
 */
export function getSimulationHintRuleIds(email: Email): string[] {
  const rules: string[] = [];

  const senderDom = domainOfEmail(email.sender_email || '');
  const subject = email.subject || '';
  const body = email.body || '';
  const links = Array.isArray(email.links) ? email.links : [];
  const atts = Array.isArray(email.attachments) ? email.attachments : [];

  // Urgency / pressure (very common + useful)
  if (URGENCY_RE.test(subject) || URGENCY_RE.test(body)) rules.push('basic.urgency');

  // Sender inconsistency / domain weirdness
  if (senderDom && /(\bsecure\b|\blogin\b|\bverify\b|\bsupport\b|\balerts\b)/i.test(senderDom)) {
    rules.push('basic.sender');
  }

  // Links (including mismatch)
  if (links.length > 0) {
    rules.push('basic.links');
    const linkHost = hostnameOfUrl(String(links[0] || ''));
    if (senderDom && linkHost && rootDomain(senderDom) !== rootDomain(linkHost)) {
      // mismatch is a strong tell
      rules.push('basic.sender');
    }
    // Subtle link patterns (subdomain traps etc.)
    if (linkHost && linkHost.split('.').length >= 4) {
      rules.push('advanced.subtle-links');
    }
  }

  // Attachments
  const bodyMentionsAttachment =
    /\battach(ed|ment|ments)?\b/i.test(body) || /\bopen attachment\b/i.test(subject);
  if (atts.length > 0 || bodyMentionsAttachment) {
    rules.push('basic.attachments');
    if (atts.some((a) => RISKY_EXT_RE.test(String(a || '')))) {
      // still covered by attachments rule; keep it simple for now
    }
  }

  // Writing / tone
  if (GENERIC_GREETING_RE.test(body)) rules.push('basic.language');

  // Reply chain spoofing
  if (REPLY_CHAIN_RE.test(body) || /^re:\s/i.test(subject) || /^fw:\s/i.test(subject)) {
    rules.push('intermediate.reply-chain');
  }

  // Workplace context / consistency (very relevant to simulator)
  rules.push('intermediate.workflow');
  rules.push('intermediate.consistency');

  // Advanced patterns
  if (PAYMENT_RE.test(subject) || PAYMENT_RE.test(body)) rules.push('advanced.bec');
  if (MFA_RE.test(subject) || MFA_RE.test(body) || CRED_RE.test(subject) || CRED_RE.test(body)) {
    rules.push('advanced.mfa-fatigue');
  }

  // Long email “credibility padding”
  if ((subject.length + body.length) > 900) rules.push('advanced.long-email');

  // De-dupe, filter disallowed, cap
  const seen = new Set<string>();
  const out: string[] = [];
  for (const r of rules) {
    if (DISALLOWED_HINT_RULE_IDS.has(r)) continue;
    if (!seen.has(r)) {
      out.push(r);
      seen.add(r);
    }
  }

  // Keep the hints tight
  return out.slice(0, 4);
}