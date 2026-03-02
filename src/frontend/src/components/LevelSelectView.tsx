import React, { useMemo, useState } from 'react';
import '../styles/MenuScreens.css';
import { fetchLevel, LevelPreview } from '../api';
import ScenarioIntroModal from './ScenarioIntroModal';
import { LEVELS } from '../levels';

interface Props {
  onStartLevel: (scenarioId: number, level: number) => void;
  onBack?: () => void;
}

const LevelSelectView: React.FC<Props> = ({ onStartLevel, onBack }) => {
  const [active, setActive] = useState<LevelPreview | null>(null);
  const [pendingLevel, setPendingLevel] = useState<number | null>(null);
  const [showScenarioModal, setShowScenarioModal] = useState(false);

  const levels = useMemo(() => LEVELS, []);

  return (
    <div className="screen-shell">
      <div className="screen-card">
        <div className="screen-header">
          <div className="brand">
            <div className="brand-badge">PA</div>
            <div>
              <h1 className="screen-title">Select a Level</h1>
              <p className="screen-subtitle">
                Choose a level to preview the scenario and start.
              </p>
            </div>
          </div>

          {onBack && (
            <button className="ms-btn ms-btn-ghost" onClick={onBack}>
              ← Back
            </button>
          )}
        </div>

        <div className="screen-body">
          <div className="level-button-grid">
            {levels.map((ld) => (
              <button
                key={ld.level}
                className="level-blue-btn"
                onClick={async () => {
                  try {
                    const data = await fetchLevel(ld.level);
                    setActive(data);
                    setPendingLevel(ld.level);
                    setShowScenarioModal(true);
                  } catch (e) {
                    console.error('Failed to load level preview', e);
                  }
                }}
              >
                Level {ld.level}
              </button>
            ))}
          </div>
        </div>
      </div>

      {showScenarioModal && active && pendingLevel !== null && (
        <ScenarioIntroModal
          scenario={active.scenario}
          level={pendingLevel}
          levelTitle={active.title}
          levelBriefing={active.briefing}
          onClose={() => {
            setShowScenarioModal(false);
            setPendingLevel(null);
          }}
          onStart={() => {
            setShowScenarioModal(false);
            const lvl = pendingLevel;
            setPendingLevel(null);
            onStartLevel(active.scenario.id, lvl);
          }}
        />
      )}
    </div>
  );
};

export default LevelSelectView;