import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitResult } from '../api';
import '../App.css';
import '../styles/InboxView.css';
import InteractionModal from './InteractionModal';


interface Props {
  onExit: () => void;
}

export const InboxView: React.FC<Props> = ({ onExit }) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selected, setSelected] = useState<Email | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  const [score, setScore] = useState(0);
  const [activeLink, setActiveLink] = useState<string | null>(null);
  const [activeAttachment, setActiveAttachment] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  
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

  const closeModal = () => {
  setActiveLink(null);
  setActiveAttachment(null);
  };

  const proceedModal = () => {
    // Simulation-only: does nothing for now.
    // Later: log a "clicked link" / "opened attachment" event.
    closeModal();
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
          {emails.map((email, i) => (
            <div
              key={email.id}
              onClick={() => setSelected(email)}
              className={`sidebar-email ${selected?.id === email.id ? 'selected' : ''}`}
            >
              <strong>{email.sender_name}</strong>
              <div>{email.subject}</div>
            </div>
          ))}
        </div>

        {/* Main content */}
        <div className="email-body">
          {selected ? (
            <>
              <div className="email-subject">{selected.subject}</div>
              <div className="email-from">
                From: {selected.sender_name} &lt;{selected.sender_email}&gt;
              </div>

              <div className="email-content">{selected.body}</div>

              {selected.links && selected.links.length > 0 && (
                <div className="email-links">
                  <h4>Links</h4>
                  <ul>
                    {selected.links.map((link, i) => (
                      <li key={i}>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveLink(link);
                            setActiveAttachment(null);
                            setShowModal(true);
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            margin: 0,
                            color: '#06c',
                            textDecoration: 'underline',
                            cursor: 'pointer',
                            font: 'inherit',
                          }}
                        >
                          {link}
                        </button>
                      </li>
                    ))}
                  </ul>
                  {(activeLink || activeAttachment) && (
                    <InteractionModal
                      type={activeLink ? 'link' : 'attachment'}
                      value={activeLink ?? activeAttachment ?? ''}
                      onClose={closeModal}
                      onProceed={proceedModal}
                    />
                )}
                </div>
              )}

              {selected.attachments && selected.attachments.length > 0 && (
                <div className="email-attachments">
                  <h4>Attachments</h4>
                  <ul>
                    {selected.attachments.map((file, i) => (
                      <li key={i}>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveAttachment(file);
                            setActiveLink(null);
                            setShowModal(true);
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            margin: 0,
                            cursor: 'pointer',
                            font: 'inherit',
                          }}
                        >
                          📎 {file}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

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
