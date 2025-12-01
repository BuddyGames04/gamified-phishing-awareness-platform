import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitResult } from '../api';
import '../App.css';
import '../styles/InboxView.css';

interface Props {
  onExit: () => void;
}

export const InboxView: React.FC<Props> = ({ onExit }) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selected, setSelected] = useState<Email | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  const [score, setScore] = useState(0);

  useEffect(() => {
    const loadEmails = async () => {
      try {
        const data = await fetchEmails();
        setEmails(data);
      } catch (err) {
        console.error('Failed to load emails:', err);
      }
    };
    loadEmails();
  }, []);

  const handleDecision = async (isPhishGuess: boolean) => {
    if (!selected) return;

    const isCorrect = selected.is_phish === isPhishGuess;
    setFeedback(isCorrect ? 'Correct' : 'Wrong');

    if (isCorrect) {
      setScore((prev) => prev + 1);
    }

    try {
      await submitResult('luke', isCorrect);
    } catch (err) {
      console.error('Error submitting result:', err);
    }

    // Reset after delay
    setTimeout(() => {
      setSelected(null);
      setFeedback('');
    }, 1200);
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '1rem' }}>
      <h1>Inbox Simulator</h1>
      <h3>Score: {score}</h3>
      <button style={{ marginBottom: '1rem' }} onClick={onExit}>
        Exit to Main Menu
      </button>

      <div className="inbox-container">
        {/* Sidebar */}
        <div className="sidebar">
          <h3 style={{ padding: '1rem' }}>Inbox</h3>
          {emails.map((email) => (
            <div
              key={email.id}
              onClick={() => setSelected(email)}
              className={`sidebar-email ${selected?.id === email.id ? 'selected' : ''}`}
            >
              <strong>{email.sender}</strong>
              <div>{email.subject}</div>
            </div>
          ))}
        </div>

        {/* Main content */}
        <div className="email-body">
          {selected ? (
            <>
              <div className="email-subject">{selected.subject}</div>
              <div className="email-from">From: {selected.sender}</div>
              <div className="email-content">{selected.body}</div>

              <div className="email-actions">
                <button onClick={() => handleDecision(true)}>Report Phish</button>
                <button onClick={() => handleDecision(false)}>Mark Safe</button>
              </div>

              {feedback && <div className="feedback">{feedback}</div>}
            </>
          ) : (
            <p>Select an email to read</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default InboxView;
