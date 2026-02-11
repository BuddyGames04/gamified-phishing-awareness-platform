import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitInteraction, submitResult } from '../api';
import '../App.css';
import '../styles/InboxView.css';
import InteractionModal from './InteractionModal';
import LevelCompleteModal from './LevelCompleteModal';

interface Props {
  onExit: () => void;
  mode: 'arcade' | 'simulation';
  userId: string;
  scenarioId?: number;
  level?: number;

  // NEW:
  username: string;
  onLogout: () => void;
}

export const InboxView: React.FC<Props> = ({
  onExit,
  mode,
  scenarioId,
  userId,
  level,
  username,
  onLogout,
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

  // used to force a full reload on replay
  const [runKey, setRunKey] = useState(0);

  useEffect(() => {
    const loadEmails = async () => {
      try {
        const { min, max } = getDifficultyWindow(level ?? 1);

        const data = await fetchEmails({
          mode,
          scenario_id: scenarioId,
          level,
          limit: 15,
        });

        setEmails(data);
        setOpenedEmailIds(new Set()); // reset per level run
        setRunTotal(data.length);
        setRunCorrect(0);
        setRunIncorrect(0);
        setShowCompleteModal(false);
        setSelected(null);
        setActiveLink(null);
        setActiveAttachment(null);
      } catch (err) {
        console.error('Failed to load emails:', err);
      }
    };

    loadEmails();
  }, [mode, scenarioId, level, runKey]);

  const handleDecision = async (isPhishGuess: boolean) => {
    if (!selected) return;

    const isCorrect = selected.is_phish === isPhishGuess;

    if (isCorrect) setRunCorrect((prev) => prev + 1);
    else setRunIncorrect((prev) => prev + 1);

    try {
      await submitResult(userId, isCorrect);
    } catch (err) {
      console.error('Error submitting result:', err);
    }
    const removedId = selected.id;
    setEmails((prev) => {
      const next = prev.filter((e) => e.id !== removedId);

      if (next.length === 0) {
        setShowCompleteModal(true);
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
    if (mode === 'simulation' && selected) {
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
      {/* Top bar */}
      <div className="outlook-topbar">
        <div className="outlook-topbar-left">
          <button className="btn" onClick={onExit}>Back</button>
          <div className="outlook-topbar-title">
            {mode === 'simulation' ? `Inbox Simulator — Level ${level ?? ''}` : 'Arcade Mode'}
          </div>
        </div>

        {/* NEW: action toolbar in the middle */}
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
                : mode === 'simulation' && !openedEmailIds.has(selected.id)
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

          <div className="user-controls">
            <span className="user-label">Signed in as {username}</span>
            <button className="btn" onClick={onLogout}>Logout</button>
          </div>
        </div>
      </div>

      <div className="outlook-main">
        {/* Left: folders (visual only) */}
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
          <div style={{ padding: '0 10px', fontSize: 12, color: 'var(--color-text-muted)' }}>
            Remaining: <strong>{emails.length}</strong>
          </div>
        </div>

        {/* Middle: list */}
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
                (email.body || '').replace(/\s+/g, ' ').slice(0, 80) + ((email.body || '').length > 80 ? '…' : '');

              // Fake time just for UI (stable per email id)
              const fakeHour = 9 + (email.id % 8);
              const fakeMin = (email.id * 7) % 60;
              const timeStr = `${String(fakeHour).padStart(2, '0')}:${String(fakeMin).padStart(2, '0')}`;

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

        {/* Right: reading pane */}
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
                            if (mode === 'simulation') {
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
                            if (mode === 'simulation') {
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

      {showCompleteModal && mode === 'simulation' && (
        <LevelCompleteModal
          title={`Level ${level ?? ''} complete`}
          subtitle="Results:"
          correct={runCorrect}
          incorrect={runIncorrect}
          total={runTotal}
          onReplay={() => setRunKey((k) => k + 1)}
          onExit={onExit}
        />
      )}
    </div>
  );
};

function getDifficultyWindow(level: number) {
  if (level <= 3) return { min: 1, max: 1 };
  if (level <= 6) return { min: 1, max: 2 };
  if (level <= 10) return { min: 1, max: 3 };
  if (level <= 15) return { min: 2, max: 4 };
  return { min: 3, max: 5 };
}

export default InboxView;
