import React, { useState } from 'react';
import './App.css';
import { InboxView } from './components/InboxView';
import ArcadeGame from './components/ArcadeGame';
import MenuView from './components/MenuView';
import LevelSelectView from './components/LevelSelectView';

type Screen = 'menu' | 'inbox' | 'arcade' | 'levels';

const App: React.FC = () => {
  const [screen, setScreen] = useState<Screen>('menu');

  const handleLevelSelect = (level: number) => {
    // Currently all levels load the same InboxView
    setScreen('inbox');
  };

  return (
    <div className="App">
      {screen === 'menu' && <MenuView navigate={setScreen} />}
      {screen === 'arcade' && <ArcadeGame onExit={() => setScreen('menu')} />}
      {screen === 'levels' && <LevelSelectView onLevelSelect={handleLevelSelect} />}
      {screen === 'inbox' && <InboxView onExit={() => setScreen('menu')} />}
    </div>
  );
};

export default App;
