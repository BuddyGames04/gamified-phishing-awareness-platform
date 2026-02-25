import React, { useState } from 'react';
import './App.css';
import { InboxView } from './components/InboxView';
import ArcadeGame from './components/ArcadeGame';
import MenuView from './components/MenuView';
import LevelSelectView from './components/LevelSelectView';
import AuthPage from './components/AuthPage';
import HamburgerMenu from './components/HamburgerMenu';
import ProfileView from './components/ProfileView';
import PvpRoot from './components/pvp/PvpRoot';
import InfoView from './components/InfoView';

type Screen = 'menu' | 'inbox' | 'arcade' | 'levels' | 'profile' | 'pvp' | 'info';

const App: React.FC = () => {
  const [screen, setScreen] = useState<Screen>('menu');
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | undefined>(
    undefined
  );
  const [selectedLevel, setSelectedLevel] = useState<number | undefined>(undefined);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [username, setUsername] = useState<string | null>(() => {
    // Restore session if token exists
    const token = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('username');
    return token && storedUser ? storedUser : null;
  });

  const handleStartLevel = (scenarioId: number, level: number) => {
    console.log('handleStartLevel', scenarioId, level);
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
      <HamburgerMenu
        open={drawerOpen}
        username={username}
        onClose={() => setDrawerOpen(false)}
        onGoProfile={() => setScreen('profile')}
        onLogout={handleLogout}
      />

      {screen === 'menu' && (
        <div style={{ position: 'absolute', top: 10, right: 10 }}>
          <button
            className="hamburger-btn"
            onClick={() => setDrawerOpen(true)}
            aria-label="Open menu"
            title="Menu"
          >
            ☰
          </button>
        </div>
      )}

      {screen === 'menu' && <MenuView navigate={setScreen} />}
      {screen === 'arcade' && (
        <ArcadeGame
          onExit={() => setScreen('menu')}
          onOpenMenu={() => setDrawerOpen(true)}
        />
      )}
      {screen === 'levels' && (
        <LevelSelectView
          onStartLevel={handleStartLevel}
          onBack={() => setScreen('menu')}
        />
      )}
      {screen === 'inbox' && (
        <InboxView
          onExit={() => setScreen('menu')}
          mode="simulation"
          userId={username}
          scenarioId={selectedScenarioId}
          level={selectedLevel}
          username={username}
          onOpenMenu={() => setDrawerOpen(true)}
        />
      )}
      {screen === 'profile' && (
        <div className="outlook-shell">
          <div className="outlook-topbar">
            <div className="outlook-topbar-left">
              <button className="btn" onClick={() => setScreen('menu')}>
                Back
              </button>
              <div className="outlook-topbar-title">Profile</div>
            </div>
            <div className="outlook-topbar-actions">
              <button
                className="hamburger-btn"
                onClick={() => setDrawerOpen(true)}
                aria-label="Open menu"
                title="Menu"
              >
                ☰
              </button>
            </div>
          </div>

          <div style={{ overflow: 'auto', flex: 1 }}>
            <ProfileView userId={username} />
          </div>
        </div>
      )}
      {screen === 'pvp' && (
        <PvpRoot
          onExitPvp={() => setScreen('menu')}
          userId={username}
          username={username}
          onOpenMenu={() => setDrawerOpen(true)}
        />
      )}
      {screen === 'info' && (
      <InfoView
        onBack={() => setScreen('menu')}
        onOpenMenu={() => setDrawerOpen(true)}
      />
    )}
    </div>
    
  );
};

export default App;
