import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitResult } from '../api';
import '../styles/InboxView.css';
import '../styles/ArcadeMode.css';

interface Props {
  onExit: () => void;
  onOpenMenu: () => void;
}

const ArcadeGame: React.FC<Props> = ({ onExit, onOpenMenu }) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    fetchEmails({ mode: 'arcade', limit: 50 }).then(setEmails).catch(console.error);
  }, []);

  const handleGuess = async (guessIsPhish: boolean) => {
    const email = emails[index];
    if (!email) return;

    const isCorrect = email.is_phish === guessIsPhish;
    setFeedback(isCorrect ? 'Correct' : 'Wrong');
    setScore((s) => s + (isCorrect ? 1 : 0));

    try {
      await submitResult('arcade', isCorrect);
    } catch (e) {
      console.error('submitResult failed', e);
    }

    setTimeout(() => {
      setFeedback(null);
      setIndex((i) => (i + 1 < emails.length ? i + 1 : 0));
    }, 900);
  };

  const email = emails[index];

  return (
    <div className="outlook-shell">
      <div className="outlook-topbar">
        <div className="outlook-topbar-left">
          <button className="btn" onClick={onExit}>Back</button>
          <div className="outlook-topbar-title">Arcade Mode</div>
        </div>

        <div className="outlook-topbar-actions">
          <div className="arcade-score-pill">
            Score: <strong>{score}</strong>
          </div>

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

      <div className="arcade-stage">
        {emails.length === 0 || !email ? (
          <div className="reading-pane">
            <div className="empty-state">Loading emails…</div>
          </div>
        ) : (
          <div className="reading-pane">
            <div className="reading-card">
              <div className="email-subject">{email.subject}</div>
              <div className="email-meta">
                From: {email.sender_name} &lt;{email.sender_email}&gt;
              </div>

              <div className="email-content">{email.body}</div>

              <div className="arcade-actions">
                <button className="btn btn-danger" onClick={() => handleGuess(true)}>
                  Phish
                </button>
                <button className="btn btn-ok" onClick={() => handleGuess(false)}>
                  Not Phish
                </button>
              </div>

              {feedback && (
                <div className={`arcade-feedback ${feedback === 'Correct' ? 'ok' : 'bad'}`}>
                  {feedback}
                </div>
              )}

              <div className="arcade-progress">
                Email {index + 1} / {emails.length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArcadeGame;
