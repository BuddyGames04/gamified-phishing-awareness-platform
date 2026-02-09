import React from 'react';
import '../styles/InboxView.css'; // or make a new css file if you prefer

type Props = {
  scenario: {
    company_name: string;
    sector: string;
    role_title: string;
    department_name: string;
    line_manager_name: string;
    responsibilities: string[];
    intro_text: string;
  };
  level: number;
  onClose: () => void;
  onStart: () => void;
};

const ScenarioIntroModal: React.FC<Props> = ({ scenario, level, onClose, onStart }) => {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.55)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: 'min(720px, 95vw)',
          background: '#fff',
          borderRadius: '10px',
          padding: '1.25rem',
          textAlign: 'left',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0 }}>
          Level {level}: Scenario Briefing
        </h2>

        <div style={{ marginBottom: '0.75rem' }}>
          <div><strong>Company:</strong> {scenario.company_name}</div>
          <div><strong>Sector:</strong> {scenario.sector}</div>
          <div><strong>Role:</strong> {scenario.role_title}</div>
          <div><strong>Department:</strong> {scenario.department_name}</div>
          <div><strong>Line Manager:</strong> {scenario.line_manager_name}</div>
        </div>

        {scenario.intro_text && (
          <p style={{ whiteSpace: 'pre-wrap' }}>{scenario.intro_text}</p>
        )}

        {scenario.responsibilities?.length > 0 && (
          <>
            <h4>Responsibilities</h4>
            <ul>
              {scenario.responsibilities.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button onClick={onClose}>Back</button>
          <button onClick={onStart}>Start Level</button>
        </div>
      </div>
    </div>
  );
};

export default ScenarioIntroModal;
