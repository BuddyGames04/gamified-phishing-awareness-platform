import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Email,
  fetchEmails,
  fetchPvpEmails,
  submitInteraction,
  submitResult,
  startLevelRun,
  completeLevelRun,
  createDecisionEvent,
} from '../api';

import { getHintLines } from '../content/infoLookup';
import { getSimulationHintRuleIds } from '../content/hintEngine';

import '../App.css';
import '../styles/InboxView.css';
import InteractionModal from './InteractionModal';
import LevelCompleteModal from './LevelCompleteModal';

import WaveToast from './WaveToast';
import { playWaveChime, primeWaveAudio } from '../utils/waveNotifier';

interface Props {
  onExit: () => void;
  mode: 'arcade' | 'simulation' | 'pvp';
  userId: string;
  scenarioId?: number;
  level?: number;
  username: string;
  onOpenMenu: () => void;
  pvpLevelId?: number;
}

export const InboxView: React.FC<Props> = ({
  onExit,
  mode,
  scenarioId,
  userId,
  level,
  username,
  onOpenMenu,
  pvpLevelId,
}) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selected, setSelected] = useState<Email | null>(null);
  const [activeLink, setActiveLink] = useState<string | null>(null);
  const [activeAttachment, setActiveAttachment] = useState<string | null>(null);
  const [openedEmailIds, setOpenedEmailIds] = useState<Set<number>>(new Set());

  const [runTotal, setRunTotal] = useState(0);
  const [runCorrect, setRunCorrect] = useState(0);
  const [runIncorrect, setRunIncorrect] = useState(0);
  const [showCompleteModal, setShowCompleteModal] = useState(false);

  const [runKey, setRunKey] = useState(0);

  const [runId, setRunId] = useState<number | null>(null);
  const [runCompleted, setRunCompleted] = useState(false);

  const [runHintRuleIds, setRunHintRuleIds] = useState<string[]>([]);

  const [incomingQueue, setIncomingQueue] = useState<Email[]>([]);
  const [waveTriggered, setWaveTriggered] = useState(false);

  const [waveToastCount, setWaveToastCount] = useState<number>(0);

  const seenEmailIdsRef = useRef<Set<number>>(new Set());

  const isHighLevel = (lvl?: number) => (lvl ?? 0) >= 3;

  const [elapsedMs, setElapsedMs] = useState(0);
  const startedAtRef = useRef<number | null>(null);

  const calcScore = useCallback(() => {
    const total = runTotal || 0;
    if (total <= 0) return 0;
    const acc = runCorrect / total;
    return Math.round(acc * 1000);
  }, [runCorrect, runTotal]);

  useEffect(() => {
    const prime = () => {
      primeWaveAudio();
      window.removeEventListener('pointerdown', prime);
      window.removeEventListener('keydown', prime);
    };
    window.addEventListener('pointerdown', prime);
    window.addEventListener('keydown', prime);
    return () => {
      window.removeEventListener('pointerdown', prime);
      window.removeEventListener('keydown', prime);
    };
  }, []);

  const triggerIncomingWave = useCallback(
    async (removedId?: number) => {
      if (mode === 'pvp' && !pvpLevelId) return;

      setWaveTriggered(true);

      const fetched =
        mode === 'pvp'
          ? await fetchPvpEmails({ level_id: pvpLevelId!, limit: 50, wave: true })
          : await fetchEmails({
              mode,
              scenario_id: scenarioId,
              level,
              limit: 50,
              wave: true,
            } as any);

      setEmails((prev) => {
        const existingIds = new Set(prev.map((e) => e.id));

        const unseen = fetched.filter((e) => {
          if (seenEmailIdsRef.current.has(e.id)) return false;
          if (existingIds.has(e.id)) return false;
          return true;
        });

        unseen.forEach((e) => seenEmailIdsRef.current.add(e.id));
        setIncomingQueue(unseen);

        if (unseen.length > 0) {
          setRunTotal((t) => t + unseen.length);
          setWaveToastCount(unseen.length);
          playWaveChime();
        }

        const remaining = removedId ? prev.filter((e) => e.id !== removedId) : prev;
        return unseen.length > 0 ? [...unseen, ...remaining] : remaining;
      });
    },
    [mode, scenarioId, level, pvpLevelId]
  );

  useEffect(() => {
    const loadEmails = async () => {
      try {
        const data =
          mode === 'pvp'
            ? await fetchPvpEmails({ level_id: pvpLevelId!, limit: 15, wave: false })
            : await fetchEmails({ mode, scenario_id: scenarioId, level, limit: 15 });

        setEmails(data);

        const nextSeen = new Set<number>();
        data.forEach((e) => nextSeen.add(e.id));
        seenEmailIdsRef.current = nextSeen;

        setOpenedEmailIds(new Set());
        setRunTotal(data.length);
        setRunCorrect(0);
        setRunIncorrect(0);
        setShowCompleteModal(false);
        setSelected(null);
        setActiveLink(null);
        setActiveAttachment(null);

        setRunHintRuleIds([]);

        setIncomingQueue([]);
        setWaveTriggered(false);

        setWaveToastCount(0);

        setRunCompleted(false);
        setRunId(null);

        if (mode === 'simulation' || mode === 'pvp') {
          try {
            const run = await startLevelRun({
              user_id: userId,
              mode,
              scenario_id: mode === 'simulation' ? scenarioId : undefined,
              level_number: mode === 'simulation' ? level ?? 1 : pvpLevelId ?? 1,
              emails_total: data.length,
              pvp_level_id: mode === 'pvp' ? pvpLevelId : undefined,
            });
            setRunId(run.id);
          } catch (e) {
            console.error('Failed to start level run', e);
          }
        }
      } catch (err) {
        console.error('Failed to load emails:', err);
      }
    };

    loadEmails();
  }, [mode, scenarioId, level, runKey, userId, pvpLevelId]);

  useEffect(() => {
    if (showCompleteModal) return;

    startedAtRef.current = Date.now();
    const reset = window.setTimeout(() => setElapsedMs(0), 0);

    const t = window.setInterval(() => {
      if (startedAtRef.current != null) {
        setElapsedMs(Date.now() - startedAtRef.current);
      }
    }, 250);

    return () => {
      window.clearTimeout(reset);
      window.clearInterval(t);
    };
  }, [runKey, mode, scenarioId, level, pvpLevelId, showCompleteModal]);

  useEffect(() => {
    if (mode !== 'simulation' && mode !== 'pvp') return;

    const timer = setTimeout(() => {
      if (!waveTriggered) {
        triggerIncomingWave().catch((e) =>
          console.error('triggerIncomingWave failed', e)
        );
      }
    }, 30000);

    return () => clearTimeout(timer);
  }, [runKey, mode, waveTriggered, triggerIncomingWave]);

  const handleDecision = async (isPhishGuess: boolean) => {
    if (!selected) return;

    const isCorrect = selected.is_phish === isPhishGuess;

    if (mode === 'simulation' && !isCorrect) {
      const ruleIds = getSimulationHintRuleIds(selected);
      if (ruleIds.length > 0) {
        setRunHintRuleIds((prev) => {
          const seen = new Set(prev);
          const next = [...prev];
          for (const r of ruleIds) {
            if (!seen.has(r)) {
              next.push(r);
              seen.add(r);
            }
          }
          return next.slice(0, 8);
        });
      }
    }

    if (isCorrect) setRunCorrect((prev) => prev + 1);
    else setRunIncorrect((prev) => prev + 1);

    try {
      await submitResult(userId, isCorrect);
    } catch (err) {
      console.error('Error submitting result:', err);
    }

    try {
      await createDecisionEvent({
        user_id: userId,
        run_id: runId,
        email_id: selected.id,
        decision: isPhishGuess
          ? 'report_phish'
          : mode === 'arcade'
            ? 'mark_safe'
            : 'mark_read',
        was_correct: isCorrect,
      });
    } catch (err) {
      console.error('Failed to create decision event:', err);
    }

    const removedId = selected.id;

    const isFinalEmail = emails.length === 1;
    if (
      (mode === 'simulation' || mode === 'pvp') &&
      isFinalEmail &&
      !waveTriggered &&
      isHighLevel(level)
    ) {
      try {
        await triggerIncomingWave(removedId);
      } catch (e) {
        console.error('triggerIncomingWave failed', e);
      }

      setSelected(null);
      setActiveLink(null);
      setActiveAttachment(null);
      return;
    }

    setEmails((prev) => {
      const next = prev.filter((e) => e.id !== removedId);

      if (next.length === 0) {
        setShowCompleteModal(true);

        if ((mode === 'simulation' || mode === 'pvp') && runId && !runCompleted) {
          const nextCorrect = isCorrect ? runCorrect + 1 : runCorrect;
          const nextIncorrect = !isCorrect ? runIncorrect + 1 : runIncorrect;

          const clientMs =
            startedAtRef.current != null
              ? Date.now() - startedAtRef.current
              : elapsedMs;

          setRunCompleted(true);
          completeLevelRun(runId, {
            correct: nextCorrect,
            incorrect: nextIncorrect,
            client_duration_ms: clientMs,
            points: calcScore(),
          } as any).catch((e) => console.error('Failed to complete level run', e));
        }
      }

      return next;
    });

    setSelected(null);
    setActiveLink(null);
    setActiveAttachment(null);
  };

  const closeModal = () => {
    setActiveLink(null);
    setActiveAttachment(null);
  };

  const proceedModal = async () => {
    if ((mode === 'simulation' || mode === 'pvp') && selected) {
      const eventType = activeLink ? 'link_click' : 'attachment_open';
      const value = activeLink ?? activeAttachment ?? null;

      try {
        if (value) {
          await submitInteraction(userId, selected.id, eventType, value);
        }
      } catch (err) {
        console.error('Error submitting interaction:', err);
      }
    }

    closeModal();
  };

  const safeLinks = selected && Array.isArray(selected.links) ? selected.links : [];
  const safeAttachments =
    selected && Array.isArray(selected.attachments) ? selected.attachments : [];

  const canAct = !!selected;

  const canMarkSafeOrRead =
    mode === 'arcade'
      ? canAct
      : canAct && selected !== null && openedEmailIds.has(selected.id);

  const safeLabel = mode === 'arcade' ? 'Mark Safe' : 'Mark as Read';

  return (
    <div className="outlook-shell">
      {waveToastCount > 0 && (
        <WaveToast count={waveToastCount} onClose={() => setWaveToastCount(0)} />
      )}

      <div className="outlook-topbar">
        <div className="outlook-topbar-left">
          <button className="btn" onClick={onExit}>
            Back
          </button>
          <div className="outlook-topbar-title">
            {mode === 'simulation'
              ? `Inbox Simulator — Level ${level ?? ''}`
              : mode === 'pvp'
                ? 'PVP — Player Level'
                : 'Arcade Mode'}
          </div>
        </div>

        <div className="outlook-topbar-center">
          <button
            className="btn btn-danger"
            disabled={!canAct}
            title={!canAct ? 'Select an email first' : ''}
            onClick={() => handleDecision(true)}
          >
            Report Phish
          </button>

          <button
            className="btn btn-ok"
            disabled={!canMarkSafeOrRead}
            title={
              !selected
                ? 'Select an email first'
                : (mode === 'simulation' || mode === 'pvp') &&
                    !openedEmailIds.has(selected.id)
                  ? 'Open the link or attachment before marking as read'
                  : ''
            }
            onClick={() => handleDecision(false)}
          >
            {safeLabel}
          </button>
        </div>

        <div className="outlook-topbar-actions">
          <input className="fake-search" placeholder="Search mail (not implemented)" />

          {(mode === 'simulation' || mode === 'pvp') && (
            <>
              <div className="arcade-score-pill">
                Time: <strong>{Math.floor(elapsedMs / 1000)}s</strong>
              </div>
              <div className="arcade-score-pill">
                Score: <strong>{calcScore()}</strong>
              </div>
            </>
          )}

          <div className="user-controls">
            <span className="user-label">Signed in as {username}</span>
            <button
              className="hamburger-btn"
              onClick={onOpenMenu}
              aria-label="Open menu"
              title="Menu"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      <div className="outlook-main">
        <div className="folder-pane">
          <div className="folder-title">Folders</div>
          <div className="folder-item active">
            <span>📥 Inbox</span>
            <span>{emails.length}</span>
          </div>
          <div className="folder-item">
            <span>📤 Sent</span>
            <span>0</span>
          </div>
          <div className="folder-item">
            <span>🗄️ Archive</span>
            <span>0</span>
          </div>

          <div className="folder-title">Session</div>
          <div
            style={{
              padding: '0 10px',
              fontSize: 12,
              color: 'var(--color-text-muted)',
            }}
          >
            Remaining: <strong>{emails.length}</strong>
          </div>
        </div>

        <div className="list-pane">
          <div className="list-header">
            <h3>Inbox</h3>
            <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
              {emails.length} items
            </div>
          </div>

          <div className="list-scroll">
            {emails.map((email) => {
              const snippet =
                (email.body || '').replace(/\s+/g, ' ').slice(0, 80) +
                ((email.body || '').length > 80 ? '…' : '');

              const fakeHour = 9 + (email.id % 8);
              const fakeMin = (email.id * 7) % 60;
              const timeStr = `${String(fakeHour).padStart(2, '0')}:${String(
                fakeMin
              ).padStart(2, '0')}`;

              return (
                <div
                  key={email.id}
                  className={`email-row ${selected?.id === email.id ? 'selected' : ''}`}
                  onClick={() => setSelected(email)}
                >
                  <div>
                    <div className="email-row-topline">
                      <div className="email-sender">{email.sender_name}</div>
                      <div className="email-subject-mini">— {email.subject}</div>
                    </div>
                    <div className="email-snippet">{snippet}</div>
                  </div>
                  <div className="email-time">{timeStr}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="reading-pane">
          {selected ? (
            <div className="reading-card">
              <div className="email-subject">{selected.subject}</div>
              <div className="email-meta">
                From: {selected.sender_name} &lt;{selected.sender_email}&gt;
              </div>

              <div className="email-content">{selected.body}</div>

              {safeLinks.length > 0 && (
                <>
                  <div className="section-title">Links</div>
                  <ul>
                    {safeLinks.map((link, i) => (
                      <li key={i}>
                        <button
                          type="button"
                          className="link-like"
                          onClick={() => {
                            if (mode === 'simulation' || mode === 'pvp') {
                              setOpenedEmailIds((prev) => {
                                const next = new Set(prev);
                                next.add(selected.id);
                                return next;
                              });
                            }
                            setActiveLink(link);
                            setActiveAttachment(null);
                          }}
                        >
                          {link}
                        </button>
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {safeAttachments.length > 0 && (
                <>
                  <div className="section-title">Attachments</div>
                  <ul>
                    {safeAttachments.map((file, i) => (
                      <li key={i}>
                        <button
                          type="button"
                          className="attachment-like"
                          onClick={() => {
                            if (mode === 'simulation' || mode === 'pvp') {
                              setOpenedEmailIds((prev) => {
                                const next = new Set(prev);
                                next.add(selected.id);
                                return next;
                              });
                            }
                            setActiveAttachment(file);
                            setActiveLink(null);
                          }}
                        >
                          📎 {file}
                        </button>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          ) : (
            <div className="empty-state">Select an email to preview</div>
          )}
        </div>
      </div>

      {(activeLink || activeAttachment) && (
        <InteractionModal
          type={activeLink ? 'link' : 'attachment'}
          value={activeLink ?? activeAttachment ?? ''}
          onClose={closeModal}
          onProceed={proceedModal}
        />
      )}

      {showCompleteModal && (mode === 'simulation' || mode === 'pvp') && (
        <LevelCompleteModal
          title={
            mode === 'pvp' ? 'PVP level complete' : `Level ${level ?? ''} complete`
          }
          subtitle="Results:"
          correct={runCorrect}
          incorrect={runIncorrect}
          total={runTotal}
          hints={getHintLines(runHintRuleIds)}
          onReplay={() => setRunKey((k) => k + 1)}
          onExit={onExit}
        />
      )}
    </div>
  );
};

export default InboxView;