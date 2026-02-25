import React, { useEffect, useMemo, useState } from 'react';
import {
  createPvpEmail,
  createPvpLevel,
  createPvpScenario,
  deletePvpLevel,
  fetchPvpMyScenarios,
  normaliseEmailPayload,
  publishPvpLevel,
  PvpScenario,
  PvpVisibility,
} from '../../api';
import EmailEditorRow, { EmailDraft } from './EmailEditorRow';
import AdversaryGuidancePanel from './AdversaryGuidancePanel';

type Props = {
  onBack: () => void;
  onCreatedAndPlay: (levelId: number) => void;
};

type Step = 'scenario' | 'level' | 'emails';

const emptyEmail = (): EmailDraft => ({
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

const PvpCreateLevel: React.FC<Props> = ({ onBack, onCreatedAndPlay }) => {
  const [step, setStep] = useState<Step>('scenario');

  // scenarios
  const [scenarios, setScenarios] = useState<PvpScenario[]>([]);
  const [useExistingScenario, setUseExistingScenario] = useState(true);
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null);

  const [scenarioForm, setScenarioForm] = useState({
    name: '',
    company_name: '',
    sector: '',
    role_title: '',
    department_name: '',
    line_manager_name: '',
    intro_text: '',
    responsibilitiesText: '', // one per line
  });

  // level
  const [levelForm, setLevelForm] = useState({
    title: '',
    briefing: '',
    visibility: 'unlisted' as PvpVisibility,
  });

  // emails
  const [emails, setEmails] = useState<EmailDraft[]>([
    emptyEmail(),
    emptyEmail(),
    emptyEmail(),
    emptyEmail(),
    emptyEmail(),
  ]);

  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchPvpMyScenarios()
      .then((data) => {
        setScenarios(data);
        if (data.length > 0) setSelectedScenarioId(data[0].id);
      })
      .catch((e) => setErr(String(e)));
  }, []);

  const totals = useMemo(() => {
    const total = emails.length;
    const waves = emails.filter((e) => e.is_wave).length;
    return { total, waves };
  }, [emails]);

  const emailErrors = useMemo(() => {
    return emails.map((e) => {
      if (!e.sender_name.trim()) return 'Sender name required';
      if (!e.sender_email.trim()) return 'Sender email required';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.sender_email.trim()))
        return 'Sender email must be a valid email address';
      if (!e.subject.trim()) return 'Subject required';
      if (!e.body.trim()) return 'Body required';
      if (!e.payloadValue.trim()) return 'Link/Attachment value required';

      if (e.payloadType === 'attachment') {
        const v = e.payloadValue.trim();
        // disallow spaces (you can auto-normalise too)
        if (/\s/.test(v))
          return 'Attachment filename cannot contain spaces (use underscores)';
        // basic filename.ext check
        if (!/^[A-Za-z0-9._-]+\.[A-Za-z0-9]{2,8}$/.test(v))
          return 'Attachment must look like a filename (e.g. invoice.pdf)';
      }

      // XOR enforced by payloadType + payloadValue, so we just ensure it exists.
      if (e.payloadType === 'link') {
        try {
          const u = new URL(e.payloadValue.trim());
          if (u.protocol !== 'http:' && u.protocol !== 'https:')
            return 'Link must be http or https';
          if (!u.hostname.includes('.')) return 'Link must include a valid hostname';
        } catch {
          return 'Link must be a valid URL';
        }
      }
      return null;
    });
  }, [emails]);

  const canProceedScenario = useMemo(() => {
    if (useExistingScenario) return !!selectedScenarioId;
    // new scenario required fields
    return (
      scenarioForm.name.trim() &&
      scenarioForm.company_name.trim() &&
      scenarioForm.sector.trim() &&
      scenarioForm.role_title.trim() &&
      scenarioForm.department_name.trim() &&
      scenarioForm.line_manager_name.trim()
    );
  }, [useExistingScenario, selectedScenarioId, scenarioForm]);

  const canProceedLevel = useMemo(() => {
    return !!levelForm.title.trim();
  }, [levelForm.title]);

  const emailsValid = useMemo(
    () => emailErrors.every((x) => x === null),
    [emailErrors]
  );

  const countValid = totals.total >= 5 && totals.total <= 20;

  const canSubmit = emailsValid && countValid;

  const createAll = async () => {
    setBusy(true);
    setErr(null);
    let createdLevel: any = null;
    try {
      // Step A: scenario id
      let scenarioId: number;

      if (useExistingScenario) {
        if (!selectedScenarioId) throw new Error('Select a scenario');
        scenarioId = selectedScenarioId;
      } else {
        const responsibilities = scenarioForm.responsibilitiesText
          .split('\n')
          .map((s) => s.trim())
          .filter(Boolean);

        const createdScenario = await createPvpScenario({
          name: scenarioForm.name,
          company_name: scenarioForm.company_name,
          sector: scenarioForm.sector,
          role_title: scenarioForm.role_title,
          department_name: scenarioForm.department_name,
          line_manager_name: scenarioForm.line_manager_name,
          intro_text: scenarioForm.intro_text,
          responsibilities,
        });

        scenarioId = createdScenario.id;
      }

      // Step B: create level
      createdLevel = await createPvpLevel({
        scenario_id: scenarioId,
        title: levelForm.title,
        briefing: levelForm.briefing,
        visibility: 'unlisted', // always start unlisted
      });

      // Step C: create emails
      // sort_order: base first, wave later. We'll auto-assign:
      // base sort: 0.. ; wave sort: 100.. (matches your simulator convention, but backend PVP uses is_wave)
      let baseIdx = 0;
      let waveIdx = 0;

      for (const draft of emails) {
        const isWave = !!draft.is_wave;
        const sort_order = isWave ? 100 + waveIdx++ : baseIdx++;

        const links = draft.payloadType === 'link' ? [draft.payloadValue] : [];
        const attachments =
          draft.payloadType === 'attachment' ? [draft.payloadValue] : [];

        const payload = normaliseEmailPayload({
          level_id: createdLevel.id,
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

        await createPvpEmail(payload);
      }

      if (levelForm.visibility === 'posted') {
        await publishPvpLevel(createdLevel.id);
      }

      onCreatedAndPlay(createdLevel.id);
    } catch (e: any) {
      if (createdLevel?.id) {
        try {
          await deletePvpLevel(createdLevel.id);
        } catch {
          /* ignore cleanup errors */
        }
      }
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
        <h2 style={{ margin: 0 }}>Create PVP Level</h2>
        <button className="btn" onClick={onBack} disabled={busy}>
          Back
        </button>
      </div>

      {err && <div style={{ marginTop: 12, color: 'salmon' }}>{err}</div>}

      <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button className="btn" onClick={() => setStep('scenario')} disabled={busy}>
          Step A: Scenario
        </button>
        <button
          className="btn"
          onClick={() => setStep('level')}
          disabled={busy || !canProceedScenario}
        >
          Step B: Level
        </button>
        <button
          className="btn"
          onClick={() => setStep('emails')}
          disabled={busy || !canProceedScenario || !canProceedLevel}
        >
          Step C: Emails
        </button>
      </div>

      <div
        style={{
          marginTop: 16,
          display: 'grid',
          gridTemplateColumns: '1fr 340px',
          gap: 14,
        }}
      >
        <div style={{ display: 'grid', gap: 12 }}>
          {step === 'scenario' && (
            <div style={{ display: 'grid', gap: 10 }}>
              <div
                style={{
                  display: 'flex',
                  gap: 12,
                  alignItems: 'center',
                  flexWrap: 'wrap',
                }}
              >
                <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    type="radio"
                    checked={useExistingScenario}
                    onChange={() => setUseExistingScenario(true)}
                  />
                  Use existing scenario
                </label>
                <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    type="radio"
                    checked={!useExistingScenario}
                    onChange={() => setUseExistingScenario(false)}
                  />
                  Create new scenario
                </label>
              </div>

              {useExistingScenario ? (
                <div style={{ display: 'grid', gap: 8 }}>
                  <div style={{ fontWeight: 700 }}>Select one of your scenarios</div>
                  <select
                    value={selectedScenarioId ?? ''}
                    onChange={(e) => setSelectedScenarioId(Number(e.target.value))}
                  >
                    {scenarios.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} — {s.company_name} ({s.role_title})
                      </option>
                    ))}
                    {scenarios.length === 0 && (
                      <option value="">No scenarios yet</option>
                    )}
                  </select>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: 10 }}>
                  <input
                    className="fake-search"
                    placeholder="Scenario name (for you)"
                    value={scenarioForm.name}
                    onChange={(e) =>
                      setScenarioForm((p) => ({ ...p, name: e.target.value }))
                    }
                  />
                  <input
                    className="fake-search"
                    placeholder="Company name"
                    value={scenarioForm.company_name}
                    onChange={(e) =>
                      setScenarioForm((p) => ({ ...p, company_name: e.target.value }))
                    }
                  />
                  <input
                    className="fake-search"
                    placeholder="Sector"
                    value={scenarioForm.sector}
                    onChange={(e) =>
                      setScenarioForm((p) => ({ ...p, sector: e.target.value }))
                    }
                  />
                  <input
                    className="fake-search"
                    placeholder="Role title"
                    value={scenarioForm.role_title}
                    onChange={(e) =>
                      setScenarioForm((p) => ({ ...p, role_title: e.target.value }))
                    }
                  />
                  <input
                    className="fake-search"
                    placeholder="Department"
                    value={scenarioForm.department_name}
                    onChange={(e) =>
                      setScenarioForm((p) => ({
                        ...p,
                        department_name: e.target.value,
                      }))
                    }
                  />
                  <input
                    className="fake-search"
                    placeholder="Line manager name"
                    value={scenarioForm.line_manager_name}
                    onChange={(e) =>
                      setScenarioForm((p) => ({
                        ...p,
                        line_manager_name: e.target.value,
                      }))
                    }
                  />
                  <textarea
                    style={{ width: '100%', minHeight: 70 }}
                    placeholder="Intro text"
                    value={scenarioForm.intro_text}
                    onChange={(e) =>
                      setScenarioForm((p) => ({ ...p, intro_text: e.target.value }))
                    }
                  />
                  <textarea
                    style={{ width: '100%', minHeight: 90 }}
                    placeholder={
                      'Responsibilities (one per line)\nExample:\nProcess invoices\nHandle supplier queries'
                    }
                    value={scenarioForm.responsibilitiesText}
                    onChange={(e) =>
                      setScenarioForm((p) => ({
                        ...p,
                        responsibilitiesText: e.target.value,
                      }))
                    }
                  />
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                <button
                  className="btn btn-ok"
                  disabled={!canProceedScenario || busy}
                  onClick={() => setStep('level')}
                >
                  Next: Level →
                </button>
              </div>
            </div>
          )}

          {step === 'level' && (
            <div style={{ display: 'grid', gap: 10 }}>
              <input
                className="fake-search"
                placeholder="Level title"
                value={levelForm.title}
                onChange={(e) => setLevelForm((p) => ({ ...p, title: e.target.value }))}
              />
              <textarea
                style={{ width: '100%', minHeight: 100 }}
                placeholder="Briefing (shown to the player)"
                value={levelForm.briefing}
                onChange={(e) =>
                  setLevelForm((p) => ({ ...p, briefing: e.target.value }))
                }
              />

              <div
                style={{
                  display: 'flex',
                  gap: 10,
                  alignItems: 'center',
                  flexWrap: 'wrap',
                }}
              >
                <div style={{ fontWeight: 700 }}>Visibility:</div>
                <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    type="radio"
                    checked={levelForm.visibility === 'unlisted'}
                    onChange={() =>
                      setLevelForm((p) => ({ ...p, visibility: 'unlisted' }))
                    }
                  />
                  Unlisted
                </label>
                <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    type="radio"
                    checked={levelForm.visibility === 'posted'}
                    onChange={() =>
                      setLevelForm((p) => ({ ...p, visibility: 'posted' }))
                    }
                  />
                  Posted
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                <button
                  className="btn"
                  onClick={() => setStep('scenario')}
                  disabled={busy}
                >
                  ← Back
                </button>
                <button
                  className="btn btn-ok"
                  disabled={!canProceedLevel || busy}
                  onClick={() => setStep('emails')}
                >
                  Next: Emails →
                </button>
              </div>
            </div>
          )}

          {step === 'emails' && (
            <div style={{ display: 'grid', gap: 12 }}>
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
                        Must be 5–20 emails
                      </span>
                    )}
                  </div>
                </div>

                <button
                  className="btn"
                  onClick={() => setEmails((prev) => [...prev, emptyEmail()])}
                  disabled={busy || emails.length >= 20}
                >
                  + Add email
                </button>
              </div>

              <div style={{ display: 'grid', gap: 10 }}>
                {emails.map((em, i) => (
                  <EmailEditorRow
                    key={i}
                    index={i}
                    value={em}
                    onChange={(next) =>
                      setEmails((prev) => prev.map((x, idx) => (idx === i ? next : x)))
                    }
                    onDelete={() =>
                      setEmails((prev) => prev.filter((_, idx) => idx !== i))
                    }
                    error={emailErrors[i]}
                  />
                ))}
              </div>

              <div style={{ display: 'grid', gap: 10 }}>
                <div style={{ fontWeight: 700 }}>Preview split</div>
                <div
                  style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}
                >
                  <div
                    style={{
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: 10,
                      padding: 10,
                    }}
                  >
                    <div style={{ fontWeight: 800, marginBottom: 6 }}>Base emails</div>
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {emails
                        .map((e, idx) => ({ e, idx }))
                        .filter(({ e }) => !e.is_wave)
                        .map(({ e, idx }) => (
                          <li key={idx} style={{ fontSize: 13 }}>
                            {e.subject || `(no subject)`} —{' '}
                            {e.sender_name || `(no sender)`}
                          </li>
                        ))}
                      {emails.filter((e) => !e.is_wave).length === 0 && (
                        <div style={{ opacity: 0.75, fontSize: 13 }}>None</div>
                      )}
                    </ul>
                  </div>

                  <div
                    style={{
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: 10,
                      padding: 10,
                    }}
                  >
                    <div style={{ fontWeight: 800, marginBottom: 6 }}>Wave emails</div>
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {emails
                        .map((e, idx) => ({ e, idx }))
                        .filter(({ e }) => e.is_wave)
                        .map(({ e, idx }) => (
                          <li key={idx} style={{ fontSize: 13 }}>
                            {e.subject || `(no subject)`} —{' '}
                            {e.sender_name || `(no sender)`}
                          </li>
                        ))}
                      {emails.filter((e) => e.is_wave).length === 0 && (
                        <div style={{ opacity: 0.75, fontSize: 13 }}>None</div>
                      )}
                    </ul>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                <button
                  className="btn"
                  onClick={() => setStep('level')}
                  disabled={busy}
                >
                  ← Back
                </button>

                <button
                  className="btn btn-danger"
                  disabled={!canSubmit || busy}
                  onClick={createAll}
                  title={!canSubmit ? 'Fix validation errors before saving' : ''}
                >
                  {busy ? 'Saving…' : 'Save & Play'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right side guidance panel */}
        <div style={{ display: 'grid', gap: 12, alignSelf: 'start' }}>
         <AdversaryGuidancePanel onBack={onBack} onPlay={onCreatedAndPlay} showBack={false} />
          <div style={{ fontSize: 12, opacity: 0.8 }}>
            Tip: waves should be “late arrivals” that pressure the player mid-run.
          </div>
        </div>
      </div>
    </div>
  );
};

export default PvpCreateLevel;
