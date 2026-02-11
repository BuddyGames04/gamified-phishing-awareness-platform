import React, { useState } from 'react';
import './App.css';
import { InboxView } from './components/InboxView';
import ArcadeGame from './components/ArcadeGame';
import MenuView from './components/MenuView';
import LevelSelectView from './components/LevelSelectView';
import AuthPage from './components/AuthPage';

type Screen = 'menu' | 'inbox' | 'arcade' | 'levels';

const App: React.FC = () => {
  const [screen, setScreen] = useState<Screen>('menu');
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | undefined>(undefined);
  const [selectedLevel, setSelectedLevel] = useState<number | undefined>(undefined);

  const [username, setUsername] = useState<string | null>(() => {
    // Restore session if token exists
    const token = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('username');
    return token && storedUser ? storedUser : null;
  });

  const handleStartLevel = (scenarioId: number, level: number) => {
    console.log("handleStartLevel", scenarioId, level);
    setSelectedScenarioId(scenarioId);
    setSelectedLevel(level);
    setScreen('inbox');
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    setUsername(null);
    setScreen('menu');
  };

  // Require auth for the app
  if (!username) {
    return (
      <div className="App">
        <AuthPage onAuthSuccess={(u) => setUsername(u)} />
      </div>
    );
  }

  return (
    <div className="App">
      {screen === 'menu' && <MenuView navigate={setScreen} />}
      {screen === 'arcade' && <ArcadeGame onExit={() => setScreen('menu')} />}
      {screen === 'levels' && <LevelSelectView onStartLevel={handleStartLevel} />}
      {screen === 'inbox' && (
        <InboxView
          onExit={() => setScreen('menu')}
          mode="simulation"
          userId={username}
          scenarioId={selectedScenarioId}
          level={selectedLevel}
          username={username}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
};

export default App;
