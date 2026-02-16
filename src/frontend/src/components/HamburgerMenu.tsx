import React from 'react';
import '../styles/HamburgerMenu.css';

type Props = {
  open: boolean;
  username: string;
  onClose: () => void;
  onGoProfile: () => void;
  onLogout: () => void;
};

const HamburgerMenu: React.FC<Props> = ({ open, username, onClose, onGoProfile, onLogout }) => {
  if (!open) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">Menu</div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-user">Signed in as <strong>{username}</strong></div>

        <button className="drawer-item" onClick={() => { onGoProfile(); onClose(); }}>
          👤 Profile & metrics
        </button>

        <button className="drawer-item danger" onClick={onLogout}>
          🚪 Logout
        </button>
      </div>
    </div>
  );
};

export default HamburgerMenu;
