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
}

export const InboxView: React.FC<Props> = ({
  onExit,
  mode,
  scenarioId,
  userId,
  level,
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

  return (
    <div style={{ textAlign: 'center', marginTop: '1rem' }}>
      <h1>Inbox Simulator</h1>
      <button style={{ marginBottom: '1rem' }} onClick={onExit}>
        Exit to Main Menu
      </button>

      <div className="inbox-container">
        {/* Sidebar */}
        <div className="sidebar">
          <h3 style={{ padding: '1rem' }}>Inbox</h3>
          {emails.map((email, i) => (
            <div
              key={email.id}
              onClick={() => setSelected(email)}
              className={`sidebar-email ${selected?.id === email.id ? 'selected' : ''}`}
            >
              <strong>{email.sender_name}</strong>
              <div>{email.subject}</div>
            </div>
          ))}
        </div>

        {/* Main content */}
        <div className="email-body">
          {selected ? (
            <>
              <div className="email-subject">{selected.subject}</div>
              <div className="email-from">
                From: {selected.sender_name} &lt;{selected.sender_email}&gt;
              </div>

              <div className="email-content">{selected.body}</div>

              {safeLinks.length > 0 && (
                <div className="email-links">
                  <h4>Links</h4>
                  <ul>
                    {safeLinks.map((link, i) => (
                      <li key={i}>
                        <button
                          type="button"
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
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            margin: 0,
                            color: '#06c',
                            textDecoration: 'underline',
                            cursor: 'pointer',
                            font: 'inherit',
                          }}
                        >
                          {link}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {safeAttachments.length > 0 && (
                <div className="email-attachments">
                  <h4>Attachments</h4>
                  <ul>
                    {safeAttachments.map((file, i) => (
                      <li key={i}>
                        <button
                          type="button"
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
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            margin: 0,
                            cursor: 'pointer',
                            font: 'inherit',
                          }}
                        >
                          📎 {file}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="email-actions">
                {mode === 'arcade' ? (
                  <>
                    <button onClick={() => handleDecision(true)}>Report Phish</button>
                    <button onClick={() => handleDecision(false)}>Mark Safe</button>
                  </>
                ) : (
                  <>
                    <button onClick={() => handleDecision(true)}>Report Phish</button>

                    <button
                      onClick={() => handleDecision(false)}
                      disabled={!selected || !openedEmailIds.has(selected.id)}
                      title={
                        !selected || openedEmailIds.has(selected.id)
                          ? ''
                          : 'Open the link or attachment before marking as read'
                      }
                    >
                      Mark as Read
                    </button>
                  </>
                )}
              </div>
            </>
          ) : (
            <p>Select an email to read</p>
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
          onReplay={() => {
            // reload the same level; emails will reappear because we re-fetch
            setRunKey((k) => k + 1);
          }}
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
