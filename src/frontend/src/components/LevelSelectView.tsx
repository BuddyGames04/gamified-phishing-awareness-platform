import React, { useEffect, useMemo, useState } from 'react';
import '../styles/MenuScreens.css';
import { fetchScenarios, Scenario } from '../api';
import ScenarioIntroModal from './ScenarioIntroModal';
import { LEVELS } from '../levels';

interface Props {
  onStartLevel: (scenarioId: number, level: number) => void;
  onBack?: () => void;
}

const LevelSelectView: React.FC<Props> = ({ onStartLevel, onBack }) => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);

  const [pendingLevel, setPendingLevel] = useState<number | null>(null);
  const [showScenarioModal, setShowScenarioModal] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchScenarios();
        setScenarios(data);
        setActiveScenario(data[0] ?? null);
      } catch (e) {
        console.error('Failed to fetch scenarios', e);
      }
    };
    load();
  }, []);

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
                onClick={() => {
                  const scenarioForLevel =
                    scenarios[Math.floor((ld.level - 1) / 2)] ?? null;

                  if (!scenarioForLevel) {
                    console.warn('No scenario found for level', ld.level);
                    return;
                  }

                  setActiveScenario(scenarioForLevel);
                  setPendingLevel(ld.level);
                  setShowScenarioModal(true);
                }}
              >
                Level {ld.level}
              </button>
            ))}
          </div>
        </div>
      </div>

      {showScenarioModal && activeScenario && pendingLevel !== null && (
        <ScenarioIntroModal
          scenario={activeScenario}
          level={pendingLevel}
          onClose={() => {
            setShowScenarioModal(false);
            setPendingLevel(null);
          }}
          onStart={() => {
            setShowScenarioModal(false);
            const lvl = pendingLevel;
            setPendingLevel(null);
            onStartLevel(activeScenario.id, lvl);
          }}
        />
      )}
    </div>
  );
};

export default LevelSelectView;
