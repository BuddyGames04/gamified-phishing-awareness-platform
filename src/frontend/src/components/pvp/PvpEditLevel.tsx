import React, { useEffect, useMemo, useState } from 'react';
import {
  createPvpEmail,
  deletePvpEmail,
  fetchPvpLevelEmails,
  normaliseEmailPayload,
  PvpLevel,
  updatePvpEmail,
  updatePvpLevel,
} from '../../api';
import EmailEditorRow, { EmailDraft } from './EmailEditorRow';

type Props = {
  level: PvpLevel;
  onBack: () => void;
};

type EditableEmailDraft = EmailDraft & { id?: number };

const toDraft = (email: any): EditableEmailDraft => {
  const links = Array.isArray(email.links) ? email.links : [];
  const attachments = Array.isArray(email.attachments) ? email.attachments : [];
  const hasLink = links.length > 0;

  return {
    id: email.id,
    sender_name: String(email.sender_name ?? ''),
    sender_email: String(email.sender_email ?? ''),
    subject: String(email.subject ?? ''),
    body: String(email.body ?? ''),
    is_phish: !!email.is_phish,
    difficulty: Number(email.difficulty ?? 3),
    category: String(email.category ?? ''),
    payloadType: hasLink ? 'link' : 'attachment',
    payloadValue: String((hasLink ? links[0] : attachments[0]) ?? ''),
    is_wave: !!email.is_wave,
  };
};

const PvpEditLevel: React.FC<Props> = ({ level, onBack }) => {
  const [title, setTitle] = useState(level.title ?? '');
  const [briefing, setBriefing] = useState(level.briefing ?? '');
  const [emails, setEmails] = useState<EditableEmailDraft[]>([]);
  const [initialEmailIds, setInitialEmailIds] = useState<number[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (level.visibility === 'posted') {
      setErr('Posted levels are locked from editing.');
      setLoading(false);
      return;
    }

    fetchPvpLevelEmails(level.id)
      .then((data) => {
        setEmails(data.map(toDraft));
        setInitialEmailIds(data.map((x) => x.id));
      })
      .catch((e) => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [level.id, level.visibility]);

  const totals = useMemo(() => {
    const total = emails.length;
    const waves = emails.filter((e) => e.is_wave).length;
    return { total, waves };
  }, [emails]);

  const emailErrors = useMemo(() => {
    return emails.map((e) => {
      if (!e.sender_name.trim()) return 'Sender name required';
      if (!e.sender_email.trim()) return 'Sender email required';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.sender_email.trim())) {
        return 'Sender email must be a valid email address';
      }
      if (!e.subject.trim()) return 'Subject required';
      if (!e.body.trim()) return 'Body required';
      if (!e.payloadValue.trim()) return 'Link/Attachment value required';

      if (e.payloadType === 'attachment') {
        const v = e.payloadValue.trim();
        if (/\s/.test(v)) return 'Attachment filename cannot contain spaces';
        if (!/^[A-Za-z0-9._-]+\.[A-Za-z0-9]{2,8}$/.test(v)) {
          return 'Attachment must look like a filename (e.g. invoice.pdf)';
        }
      }

      if (e.payloadType === 'link') {
        try {
          const u = new URL(e.payloadValue.trim());
          if (u.protocol !== 'http:' && u.protocol !== 'https:') {
            return 'Link must be http or https';
          }
          if (!u.hostname.includes('.')) return 'Link must include a valid hostname';
        } catch {
          return 'Link must be a valid URL';
        }
      }

      return null;
    });
  }, [emails]);

  const emailsValid = useMemo(
    () => emailErrors.every((x) => x === null),
    [emailErrors]
  );
  const countValid = useMemo(
    () => totals.total >= 5 && totals.total <= 20,
    [totals.total]
  );

  const canSave =
    !!title.trim() &&
    emailsValid &&
    countValid &&
    !loading &&
    level.visibility !== 'posted';

  const emptyEmail = (): EditableEmailDraft => ({
    sender_name: '',
    sender_email: '',
    subject: '',
    body: '',
    is_phish: false,
    difficulty: 3,
    category: '',
    payloadType: 'link',
    payloadValue: '',
    is_wave: false,
  });

  const saveAll = async () => {
    setBusy(true);
    setErr(null);

    try {
      await updatePvpLevel(level.id, {
        title: title.trim(),
        briefing,
      });

      const currentIds = new Set(emails.map((e) => e.id).filter(Boolean) as number[]);
      for (const oldId of initialEmailIds) {
        if (!currentIds.has(oldId)) {
          await deletePvpEmail(level.id, oldId);
        }
      }

      let baseIdx = 0;
      let waveIdx = 0;

      for (const draft of emails) {
        const isWave = !!draft.is_wave;
        const sort_order = isWave ? 100 + waveIdx++ : baseIdx++;

        const links = draft.payloadType === 'link' ? [draft.payloadValue] : [];
        const attachments =
          draft.payloadType === 'attachment' ? [draft.payloadValue] : [];

        const payload = normaliseEmailPayload({
          sender_name: draft.sender_name,
          sender_email: draft.sender_email,
          subject: draft.subject,
          body: draft.body,
          is_phish: draft.is_phish,
          difficulty: draft.difficulty,
          category: draft.category?.trim() || null,
          links,
          attachments,
          is_wave: isWave,
          sort_order,
        });

        if (draft.id) {
          await updatePvpEmail(level.id, draft.id, payload);
        } else {
          await createPvpEmail({ level_id: level.id, ...payload });
        }
      }

      onBack();
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: 18, maxWidth: 1200, margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <h2 style={{ margin: 0 }}>Edit Level</h2>
        <button className="btn" onClick={onBack} disabled={busy}>
          Back
        </button>
      </div>

      {err && <div style={{ marginTop: 12, color: 'salmon' }}>{err}</div>}

      <div style={{ marginTop: 16, display: 'grid', gap: 10 }}>
        <input
          className="fake-search"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Level title"
          disabled={busy || loading}
        />
        <textarea
          style={{ width: '100%', minHeight: 100 }}
          value={briefing}
          onChange={(e) => setBriefing(e.target.value)}
          placeholder="Briefing"
          disabled={busy || loading}
        />
      </div>

      <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            gap: 12,
            flexWrap: 'wrap',
          }}
        >
          <div>
            <div style={{ fontWeight: 800 }}>Emails Builder</div>
            <div style={{ fontSize: 13, opacity: 0.85 }}>
              Total: <strong>{totals.total}</strong> • Waves:{' '}
              <strong>{totals.waves}</strong>{' '}
              {!countValid && (
                <span style={{ color: 'salmon', marginLeft: 8 }}>
                  Must be 5-20 emails
                </span>
              )}
            </div>
          </div>

          <button
            className="btn"
            onClick={() => setEmails((prev) => [...prev, emptyEmail()])}
            disabled={busy || loading || emails.length >= 20}
          >
            + Add email
          </button>
        </div>

        {loading ? (
          <div style={{ opacity: 0.8 }}>Loading emails...</div>
        ) : (
          <div style={{ display: 'grid', gap: 10 }}>
            {emails.map((em, i) => (
              <EmailEditorRow
                key={em.id ?? i}
                index={i}
                value={em}
                onChange={(next) =>
                  setEmails((prev) => prev.map((x, idx) => (idx === i ? next : x)))
                }
                onDelete={() => setEmails((prev) => prev.filter((_, idx) => idx !== i))}
                error={emailErrors[i]}
              />
            ))}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button
            className="btn btn-danger"
            disabled={!canSave || busy}
            onClick={saveAll}
          >
            {busy ? 'Saving...' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PvpEditLevel;
