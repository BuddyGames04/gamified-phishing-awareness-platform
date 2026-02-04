import React from 'react';

interface Props {
  onLevelSelect: (level: number) => void;
}

const LevelSelectView: React.FC<Props> = ({ onLevelSelect }) => {
  return (
    <div className="level-select-view">
      <h2>Select a Level</h2>
      <div className="level-buttons">
        {[1, 2, 3].map((level) => (
          <button key={level} onClick={() => onLevelSelect(level)}>
            Level {level}
          </button>
        ))}
      </div>
    </div>
  );
};

export default LevelSelectView;
