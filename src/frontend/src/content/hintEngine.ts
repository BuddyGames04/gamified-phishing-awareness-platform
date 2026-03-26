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

const RISKY_EXT_RE = /\.(exe|js|bat|cmd|scr|msi|ps1|vbs|jar|docm|xlsm|pptm|zip|rar)\b/i;

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

const DISALLOWED_HINT_RULE_IDS = new Set<string>([
  'about.core-loop',
  'about.arcade',
  'about.simulator',
  'about.pvp',
  'phish.definition',
  'phish.social-engineering',
  'phish.not-just-email',
  'intermediate.login-path',
  'intermediate.secondary-channel',
  'adversary.defender-habit',
]);

export function getSimulationHintRuleIds(email: Email): string[] {
  const rules: string[] = [];

  const senderDom = domainOfEmail(email.sender_email || '');
  const subject = email.subject || '';
  const body = email.body || '';
  const links = Array.isArray(email.links) ? email.links : [];
  const atts = Array.isArray(email.attachments) ? email.attachments : [];

  if (URGENCY_RE.test(subject) || URGENCY_RE.test(body)) rules.push('basic.urgency');

  if (
    senderDom &&
    /(\bsecure\b|\blogin\b|\bverify\b|\bsupport\b|\balerts\b)/i.test(senderDom)
  ) {
    rules.push('basic.sender');
  }

  if (links.length > 0) {
    rules.push('basic.links');
    const linkHost = hostnameOfUrl(String(links[0] || ''));
    if (senderDom && linkHost && rootDomain(senderDom) !== rootDomain(linkHost)) {
      rules.push('basic.sender');
    }
    if (linkHost && linkHost.split('.').length >= 4) {
      rules.push('advanced.subtle-links');
    }
  }

  const bodyMentionsAttachment =
    /\battach(ed|ment|ments)?\b/i.test(body) || /\bopen attachment\b/i.test(subject);
  if (atts.length > 0 || bodyMentionsAttachment) {
    rules.push('basic.attachments');
    if (atts.some((a) => RISKY_EXT_RE.test(String(a || '')))) {
    void 0;
    }
  }

  if (GENERIC_GREETING_RE.test(body)) rules.push('basic.language');

  if (REPLY_CHAIN_RE.test(body) || /^re:\s/i.test(subject) || /^fw:\s/i.test(subject)) {
    rules.push('intermediate.reply-chain');
  }

  rules.push('intermediate.workflow');
  rules.push('intermediate.consistency');

  if (PAYMENT_RE.test(subject) || PAYMENT_RE.test(body)) rules.push('advanced.bec');
  if (
    MFA_RE.test(subject) ||
    MFA_RE.test(body) ||
    CRED_RE.test(subject) ||
    CRED_RE.test(body)
  ) {
    rules.push('advanced.mfa-fatigue');
  }

  if (subject.length + body.length > 900) rules.push('advanced.long-email');

  const seen = new Set<string>();
  const out: string[] = [];
  for (const r of rules) {
    if (DISALLOWED_HINT_RULE_IDS.has(r)) continue;
    if (!seen.has(r)) {
      out.push(r);
      seen.add(r);
    }
  }

  return out.slice(0, 4);
}
