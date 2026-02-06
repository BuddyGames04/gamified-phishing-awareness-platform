import React from 'react';
import { Scenario } from '../api';

export default function ScenarioBriefing(props: {
  scenario: Scenario;
  userDisplayName: string;
  onStart: () => void;
  onBack: () => void;
}) {
  const { scenario, userDisplayName, onStart, onBack } = props;

  return (
    <div style={{ maxWidth: 720, margin: '2rem auto', textAlign: 'left' }}>
      <h1>Workday Briefing</h1>

      <p>
        <strong>Company:</strong> {scenario.company_name} ({scenario.sector})
      </p>
      <p>
        <strong>Your role:</strong> {scenario.role_title}
      </p>
      <p>
        <strong>Department:</strong> {scenario.department_name}
      </p>
      <p>
        <strong>Line manager:</strong> {scenario.line_manager_name}
      </p>
      <p>
        <strong>You are:</strong> {userDisplayName}
      </p>

      {scenario.intro_text && (
        <>
          <h3>Context</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{scenario.intro_text}</p>
        </>
      )}

      <h3>Responsibilities</h3>
      <ul>{scenario.responsibilities?.map((r, i) => <li key={i}>{r}</li>)}</ul>

      <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
        <button onClick={onBack}>Back</button>
        <button onClick={onStart}>Start Workday</button>
      </div>
    </div>
  );
}
