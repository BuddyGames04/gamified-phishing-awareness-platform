import React from 'react';
import '../../styles/MenuScreens.css';

type Props = {
  onBack: () => void;
  onBrowsePosted: () => void;
  onMyLevels: () => void;
  onCreate: () => void;
};

const PvpMenu: React.FC<Props> = ({ onBack, onBrowsePosted, onMyLevels, onCreate }) => {
  return (
    <div className="screen-shell">
      <div className="screen-card">
        <div className="screen-header">
          <div className="brand">
            <div className="brand-badge">⚔️</div>
            <div>
              <h1 className="screen-title">PVP</h1>
              <p className="screen-subtitle">
                Create your own phishing simulations and test other players.
              </p>
            </div>
          </div>

          <div className="top-right-hint">Build • Publish • Play</div>
        </div>

        <div className="screen-body">
          <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
            <button className="btn" onClick={onBack}>
              Back
            </button>
          </div>

          <div className="menu-grid">
            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={onBrowsePosted}
              onKeyDown={(e) => e.key === 'Enter' && onBrowsePosted()}
            >
              <div className="action-icon primary">🎯</div>
              <div>
                <div className="action-title">Play challenge levels</div>
                <div className="action-desc">Browse posted player levels.</div>
              </div>
            </div>

            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={onMyLevels}
              onKeyDown={(e) => e.key === 'Enter' && onMyLevels()}
            >
              <div className="action-icon secondary">📦</div>
              <div>
                <div className="action-title">Load your levels</div>
                <div className="action-desc">View/edit your saved levels.</div>
              </div>
            </div>

            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={onCreate}
              onKeyDown={(e) => e.key === 'Enter' && onCreate()}
            >
              <div className="action-icon warning">✍️</div>
              <div>
                <div className="action-title">Create level</div>
                <div className="action-desc">Build a scenario + level + emails.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PvpMenu;
