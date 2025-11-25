import React, { useState } from 'react';
import './App.css';
import InboxView from './components/InboxView';
import ArcadeMode from './components/ArcadeMode';

const App: React.FC = () => {
  const [mode, setMode] = useState<'inbox' | 'arcade'>('inbox');

  return (
    <div className="App">
      <header className="app-header">
        <h1 className="app-title">Phishing Awareness Platform</h1>
        <div className="mode-switch">
          <button
            onClick={() => setMode('inbox')}
            className={mode === 'inbox' ? 'active' : ''}
          >
            Inbox Mode
          </button>
          <button
            onClick={() => setMode('arcade')}
            className={mode === 'arcade' ? 'active' : ''}
          >
            Arcade Mode
          </button>
        </div>
      </header>

      {mode === 'inbox' ? <InboxView /> : <ArcadeMode />}
    </div>
  );
};

export default App;
