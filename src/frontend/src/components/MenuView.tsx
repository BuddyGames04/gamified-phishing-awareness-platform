import React from 'react';
import '../styles/MenuScreens.css';

interface Props {
  navigate: (screen: 'menu' | 'inbox' | 'arcade' | 'levels' | 'pvp' | 'info') => void;
}

const MenuView: React.FC<Props> = ({ navigate }) => {
  return (
    <div className="screen-shell">
      <div className="screen-card">
        <div className="screen-header">
          <div className="brand">
            <div className="brand-badge">PA</div>
            <div>
              <h1 className="screen-title">Phishing Awareness Platform</h1>
              <p className="screen-subtitle">
                Train detection skills with realistic inbox simulations and fast-paced
                arcade rounds.
              </p>
            </div>
          </div>

          <div className="top-right-hint">Tip: check your metrics via ☰</div>
        </div>

        <div className="screen-body">
          <div className="menu-grid">
            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate('levels')}
              onKeyDown={(e) => e.key === 'Enter' && navigate('levels')}
            >
              <div className="action-icon primary">📥</div>
              <div>
                <div className="action-title">Inbox Simulator</div>
                <div className="action-desc">
                  Scenario-based levels. Learn safe patterns under “work-like” pressure.
                </div>
              </div>
            </div>

            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate('arcade')}
              onKeyDown={(e) => e.key === 'Enter' && navigate('arcade')}
            >
              <div className="action-icon secondary">🕹️</div>
              <div>
                <div className="action-title">Arcade Mode</div>
                <div className="action-desc">
                  Quickfire decisions. Great for warm-ups and repeated practice.
                </div>
              </div>
            </div>

            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate('pvp')}
              onKeyDown={(e) => e.key === 'Enter' && navigate('pvp')}
            >
              <div className="action-icon warning">⚔️</div>
              <div>
                <div className="action-title">PVP</div>
                <div className="action-desc">
                  Create and play player-made challenge levels.
                </div>
              </div>
            </div>

            <div className="action-card disabled" aria-disabled="true">
              <div className="action-icon primary">🏆</div>
              <div>
                <div className="action-title">Leaderboard</div>
                <div className="action-desc">Under construction (coming soon).</div>
              </div>
            </div>

            <div
              className="action-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate('info')}
              onKeyDown={(e) => e.key === 'Enter' && navigate('info')}
            >
              <div className="action-icon secondary">ℹ️</div>
              <div>
                <div className="action-title">Info</div>
                <div className="action-desc">
                  A practical tutorial on phishing and how to spot it — from beginner to
                  advanced.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MenuView;
