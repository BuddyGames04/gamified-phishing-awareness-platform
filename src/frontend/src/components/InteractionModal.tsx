import React from 'react';
import '../styles/InteractionModal.css';

type InteractionType = 'link' | 'attachment';

interface Props {
  type: InteractionType;
  value: string;
  onClose: () => void;
  onProceed?: () => void;
}

const InteractionModal: React.FC<Props> = ({ type, value, onClose, onProceed }) => {
  const title = type === 'link' ? 'Open link?' : 'Open attachment?';
  const label = type === 'link' ? 'URL' : 'File';

  return (
    <div
      className="interaction-modal-overlay"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="interaction-modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginTop: 0 }}>{title}</h3>

        <p style={{ marginBottom: '0.5rem' }}>
          <strong>{label}:</strong>
        </p>

        <div className="interaction-modal-value">{value}</div>

        <div className="interaction-modal-actions">
          <button type="button" onClick={onClose}>
            Cancel
          </button>

          {onProceed && (
            <button type="button" onClick={onProceed}>
              Proceed
            </button>
          )}
        </div>

        <p className="interaction-modal-hint">
          (Simulation: this won’t actually open anything.)
        </p>
      </div>
    </div>
  );
};

export default InteractionModal;
