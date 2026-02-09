import React, { useState } from 'react';
import './App.css';
import { InboxView } from './components/InboxView';
import ArcadeGame from './components/ArcadeGame';
import MenuView from './components/MenuView';
import LevelSelectView from './components/LevelSelectView';

type Screen = 'menu' | 'inbox' | 'arcade' | 'levels';

const App: React.FC = () => {
  const [screen, setScreen] = useState<Screen>('menu');
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | undefined>(undefined);
  const [selectedLevel, setSelectedLevel] = useState<number | undefined>(undefined);

  const handleStartLevel = (scenarioId: number, level: number) => {
    setSelectedScenarioId(scenarioId);
    setSelectedLevel(level);
    setScreen('inbox');
  };

  return (
    <div className="App">
      {screen === 'menu' && <MenuView navigate={setScreen} />}
      {screen === 'arcade' && <ArcadeGame onExit={() => setScreen('menu')} />}
      {screen === 'levels' && <LevelSelectView onStartLevel={handleStartLevel} />}
      {screen === 'inbox' && (
        <InboxView
          onExit={() => setScreen('menu')}
          mode="simulation"
          userId="luke"
          scenarioId={selectedScenarioId}
          level={selectedLevel}
        />
      )}
    </div>
  );
};

export default App;
