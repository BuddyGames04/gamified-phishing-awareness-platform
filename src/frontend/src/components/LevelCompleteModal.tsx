import React from 'react';
import '../styles/LevelCompleteModal.css';

type HintLine = { id: string; title: string; summary?: string };

interface Props {
  title: string;
  subtitle?: string;
  correct: number;
  incorrect: number;
  total: number;
  onReplay: () => void;
  onExit: () => void;

  // NEW
  hints?: HintLine[];
  timeSeconds?: number;
  score?: number;
}

const LevelCompleteModal: React.FC<Props> = ({
  title,
  subtitle,
  correct,
  incorrect,
  total,
  onReplay,
  onExit,
  hints,
  score,
  timeSeconds,
}) => {
  const safeTotal = Math.max(total, correct + incorrect);
  const accuracy = safeTotal > 0 ? Math.round((correct / safeTotal) * 100) : 0;

  return (
    <div className="level-complete-backdrop" role="dialog" aria-modal="true">
      <div className="level-complete-modal">
        <h2>{title}</h2>
        {subtitle && <p className="subtitle">{subtitle}</p>}

        <div className="stats">
          <div>
            <strong>Total:</strong> {safeTotal}
          </div>
          <div>
            <strong>Correct:</strong> {correct}
          </div>
          <div>
            <strong>Incorrect:</strong> {incorrect}
          </div>
          <div>
            <strong>Accuracy:</strong> {accuracy}%
          </div>
          {typeof timeSeconds === 'number' && (
            <div><strong>Time:</strong> {timeSeconds}s</div>
          )}

          {typeof score === 'number' && (
            <div><strong>Score:</strong> {score}</div>
          )}
        </div>

        {/* NEW: Hints */}
        {hints && hints.length > 0 && (
          <div style={{ marginTop: 14, textAlign: 'left' }}>
            <div style={{ fontWeight: 800, marginBottom: 6 }}>
              What to watch for next time
            </div>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {hints.map((h) => (
                <li key={h.id} style={{ marginBottom: 6 }}>
                  <strong>{h.title}</strong>
                  {h.summary ? ` — ${h.summary}` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="actions">
          <button onClick={onReplay}>Replay level</button>
          <button onClick={onExit}>Exit</button>
        </div>
      </div>
    </div>
  );
};

export default LevelCompleteModal;
