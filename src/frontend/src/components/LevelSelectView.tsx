import React, { useEffect, useMemo, useState } from 'react';
import { fetchScenarios, Scenario } from '../api';
import ScenarioIntroModal from './ScenarioIntroModal';
import { LEVELS } from '../levels';

interface Props {
  onStartLevel: (scenarioId: number, level: number) => void;
}

const LevelSelectView: React.FC<Props> = ({ onStartLevel }) => {
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

    const scenarioById = useMemo(() => {
    const map = new Map<number, Scenario>();
    scenarios.forEach((s) => map.set(s.id, s));
    return map;
  }, [scenarios]);

  const levels = useMemo(() => LEVELS, []);

  return (
    <div className="level-select-view">
      <h2>Select a Level</h2>

      <div className="level-buttons" style={{ marginTop: '1rem' }}>
        {levels.map((ld) => (
          <button
            key={ld.level}
            onClick={() => {
              const mapped = scenarios.find((s) => s.id === ld.scenarioId) ?? activeScenario;
              if (!mapped) return;
              setActiveScenario(mapped);
              setPendingLevel(ld.level);
              setShowScenarioModal(true);
            }}
          >
            Level {ld.level}
          </button>
        ))}
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
            const level = pendingLevel;
            setPendingLevel(null);
            onStartLevel(activeScenario.id, level as number);
          }}
        />
      )}
    </div>
  );
};

export default LevelSelectView;
