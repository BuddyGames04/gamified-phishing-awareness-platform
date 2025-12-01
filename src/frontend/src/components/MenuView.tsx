import React from 'react';

interface Props {
  navigate: (screen: 'menu' | 'inbox' | 'arcade' | 'levels') => void;
}

const MenuView: React.FC<Props> = ({ navigate }) => {
  return (
    <div className="menu-view">
      <h1>Phishing Awareness Platform</h1>
      <button onClick={() => navigate('levels')}>Play Inbox Simulator Levels</button>
      <button onClick={() => navigate('arcade')}>Arcade Mode</button>
      <button disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
        PVP (under construction)
      </button>
    </div>
  );
};

export default MenuView;
