// src/frontend/src/components/ArcadeGame.tsx
import React, { useEffect, useRef, useState } from 'react';
import { ArcadeNextEmail, fetchArcadeNext, postArcadeAttempt } from '../api';
import '../styles/InboxView.css';
import '../styles/ArcadeMode.css';
import { getHintLines } from '../content/infoLookup';

interface Props {
  onExit: () => void;
  onOpenMenu: () => void;
}

type Phase = 'answer' | 'review';

const ArcadeGame: React.FC<Props> = ({ onExit, onOpenMenu }) => {
  const [email, setEmail] = useState<ArcadeNextEmail | null>(null);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const startedAtRef = useRef<number>(Date.now());

  const [hintTitle, setHintTitle] = useState<string | null>(null);
  const [hintRules, setHintRules] = useState<string[]>([]);

  const [phase, setPhase] = useState<Phase>('answer');
  const [answering, setAnswering] = useState(false);

  const loadNext = async () => {
    setLoading(true);
    try {
      const next = await fetchArcadeNext();
      setEmail(next);
      startedAtRef.current = Date.now();

      // reset UI state for the next email
      setFeedback(null);
      setHintTitle(null);
      setHintRules([]);
      setPhase('answer');
      setAnswering(false);
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
    if (answering || phase !== 'answer') return;

    setAnswering(true);

    const responseTimeMs = Date.now() - startedAtRef.current;
    const isCorrect = email.is_phish === guessIsPhish;

    setFeedback(isCorrect ? 'Correct' : 'Wrong');
    setScore((s) => s + (isCorrect ? 1 : 0));

    try {
      const attempt: any = await postArcadeAttempt({
        email_id: email.id,
        guess_is_phish: guessIsPhish,
        response_time_ms: responseTimeMs,
      });

      setHintTitle(attempt?.hint_title ?? null);
      setHintRules(Array.isArray(attempt?.hint_rule_ids) ? attempt.hint_rule_ids : []);
    } catch (e) {
      console.error('postArcadeAttempt failed', e);
      // still allow review/next even if hints fail
      setHintTitle(null);
      setHintRules([]);
    } finally {
      setPhase('review');
      setAnswering(false);
    }
  };

  const canAnswer = phase === 'answer' && !answering && !loading && !!email;
  const canNext = phase === 'review' && !loading;

  return (
    <div className="outlook-shell">
      <div className="outlook-topbar">
        <div className="outlook-topbar-left">
          <button className="btn" onClick={onExit}>
            Back
          </button>
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

              {(email.attachments?.length || email.links?.length) ? (
                <div style={{ marginTop: 8, fontSize: 13, opacity: 0.9 }}>
                  {email.attachments && email.attachments.length > 0 && (
                    <div>
                      <strong>Attachments:</strong> {email.attachments.join(', ')}
                    </div>
                  )}
                  {email.links && email.links.length > 0 && (
                    <div>
                      <strong>Links:</strong> {email.links.join(', ')}
                    </div>
                  )}
                </div>
              ) : null}

              <div className="email-content">{email.body}</div>

              <div className="arcade-actions">
                <button
                  className="btn btn-danger"
                  onClick={() => handleGuess(true)}
                  disabled={!canAnswer}
                >
                  Phish
                </button>
                <button
                  className="btn btn-ok"
                  onClick={() => handleGuess(false)}
                  disabled={!canAnswer}
                >
                  Not Phish
                </button>

                <button
                  className="btn"
                  onClick={loadNext}
                  disabled={!canNext}
                  title={phase !== 'review' ? 'Answer first to continue' : 'Next email'}
                >
                  Next →
                </button>
              </div>

              {feedback && (
                <div className={`arcade-feedback ${feedback === 'Correct' ? 'ok' : 'bad'}`}>
                  {feedback}
                </div>
              )}

              {/* Show hints in review phase (so they persist until Next) */}
              {phase === 'review' && feedback === 'Wrong' && hintRules.length > 0 && (
                <div style={{ marginTop: 10, fontSize: 13, opacity: 0.95 }}>
                  <div style={{ fontWeight: 800, marginBottom: 6 }}>
                    {hintTitle ?? 'Hint'}
                  </div>

                  {!email.is_phish && (
                    <div style={{ marginBottom: 6, opacity: 0.9 }}>
                      Being cautious is good — aim to verify rather than guess.
                    </div>
                  )}

                  <ul style={{ margin: 0, paddingLeft: 18 }}>
                    {getHintLines(hintRules).map((h) => (
                      <li key={h.id}>
                        <strong>{h.title}</strong>
                        {h.summary ? ` — ${h.summary}` : ''}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* tiny debug pill (remove later) */}
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