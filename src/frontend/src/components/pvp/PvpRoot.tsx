import React, { useState } from 'react';
import PvpMenu from './PvpMenu';
import PvpBrowsePosted from './PvpBrowsePosted';
import PvpMyLevels from './PvpMyLevels';
import PvpCreateLevel from './PvpCreateLevel';
import InboxView from '../InboxView';

type Screen = 'menu' | 'posted' | 'mine' | 'create' | 'play';

type Props = {
  onExitPvp: () => void;
  userId: string;
  username: string;
  onOpenMenu: () => void;
};

const PvpRoot: React.FC<Props> = ({ onExitPvp, userId, username, onOpenMenu }) => {
  const [screen, setScreen] = useState<Screen>('menu');
  const [playingLevelId, setPlayingLevelId] = useState<number | null>(null);

  const play = (levelId: number) => {
    setPlayingLevelId(levelId);
    setScreen('play');
  };

  const PvpHamburgerButton = (
    <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 50 }}>
      <button
        className="hamburger-btn"
        onClick={onOpenMenu}
        aria-label="Open menu"
        title="Menu"
      >
        ☰
      </button>
    </div>
  );

  if (screen === 'play' && playingLevelId) {
    return (
      <InboxView
        onExit={() => setScreen('menu')}
        mode="pvp"
        userId={userId}
        username={username}
        onOpenMenu={onOpenMenu}
        pvpLevelId={playingLevelId}
      />
    );
  }

  if (screen === 'posted') {
    return (
      <>
        {PvpHamburgerButton}
        <PvpBrowsePosted onBack={() => setScreen('menu')} onPlay={play} />
      </>
    );
  }

  if (screen === 'mine') {
    return (
      <>
        {PvpHamburgerButton}
        <PvpMyLevels onBack={() => setScreen('menu')} onPlay={play} />
      </>
    );
  }

  if (screen === 'create') {
    return (
      <>
        {PvpHamburgerButton}
        <PvpCreateLevel
          onBack={() => setScreen('menu')}
          onCreatedAndPlay={(levelId) => play(levelId)}
        />
      </>
    );
  }

  return (
    <>
      {PvpHamburgerButton}
      <PvpMenu
        onBack={onExitPvp}
        onBrowsePosted={() => setScreen('posted')}
        onMyLevels={() => setScreen('mine')}
        onCreate={() => setScreen('create')}
      />
    </>
  );
};

export default PvpRoot;