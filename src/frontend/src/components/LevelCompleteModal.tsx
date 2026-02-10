import React from 'react';
import '../styles/LevelCompleteModal.css';

interface Props {
  title: string;
  subtitle?: string;
  correct: number;
  incorrect: number;
  total: number;
  onReplay: () => void;
  onExit: () => void;
}

const LevelCompleteModal: React.FC<Props> = ({
  title,
  subtitle,
  correct,
  incorrect,
  total,
  onReplay,
  onExit,
}) => {
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0;

  return (
    <div className="level-complete-backdrop" role="dialog" aria-modal="true">
      <div className="level-complete-modal">
        <h2>{title}</h2>
        {subtitle && <p className="subtitle">{subtitle}</p>}

        <div className="stats">
          <div>
            <strong>Total:</strong> {total}
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
        </div>

        <div className="actions">
          <button onClick={onReplay}>Replay level</button>
          <button onClick={onExit}>Exit</button>
        </div>
      </div>
    </div>
  );
};

export default LevelCompleteModal;
