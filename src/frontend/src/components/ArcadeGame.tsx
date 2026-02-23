import React, { useEffect, useRef, useState } from 'react';
import { ArcadeNextEmail, fetchArcadeNext, postArcadeAttempt } from '../api';
import '../styles/InboxView.css';
import '../styles/ArcadeMode.css';

interface Props {
  onExit: () => void;
  onOpenMenu: () => void;
}

const ArcadeGame: React.FC<Props> = ({ onExit, onOpenMenu }) => {
  const [email, setEmail] = useState<ArcadeNextEmail | null>(null);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const startedAtRef = useRef<number>(Date.now());

  const loadNext = async () => {
    setLoading(true);
    try {
      const next = await fetchArcadeNext();
      setEmail(next);
      startedAtRef.current = Date.now();
    } catch (e) {
      console.error(e);
      setEmail(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNext();
  }, []);

  const handleGuess = async (guessIsPhish: boolean) => {
    if (!email) return;

    const responseTimeMs = Date.now() - startedAtRef.current;
    const isCorrect = email.is_phish === guessIsPhish;

    setFeedback(isCorrect ? 'Correct' : 'Wrong');
    setScore((s) => s + (isCorrect ? 1 : 0));

    try {
      await postArcadeAttempt({
        email_id: email.id,
        guess_is_phish: guessIsPhish,
        response_time_ms: responseTimeMs,
      });
    } catch (e) {
      console.error('postArcadeAttempt failed', e);
    }

    setTimeout(() => {
      setFeedback(null);
      loadNext();
    }, 900);
  };

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
        {loading || !email ? (
          <div className="reading-pane">
            <div className="empty-state">
              {loading ? 'Loading email…' : 'No arcade emails available.'}
            </div>
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

              {/*tiny debug pill (remove later) */}
              <div className="arcade-progress">
                Target difficulty: {email.target_difficulty_int} ({email.target_difficulty.toFixed(1)})
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArcadeGame;