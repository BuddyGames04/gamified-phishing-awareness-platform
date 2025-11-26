import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitResult } from '../api';
import '../App.css';
import '../styles/ArcadeMode.css';

const ArcadeMode: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    fetchEmails().then(setEmails);
  }, []);

  const handleGuess = async (guess: boolean) => {
    const email = emails[index];
    const isCorrect = email.is_phish === guess;
    setFeedback(isCorrect ? 'Correct!' : 'Wrong');
    setScore((s) => s + (isCorrect ? 1 : 0));

    await submitResult('luke', isCorrect);

    setTimeout(() => {
      setFeedback('');
      setIndex((i) => (i + 1 < emails.length ? i + 1 : 0));
    }, 1200);
  };

  if (emails.length === 0) return <p>Loading emails...</p>;
  const email = emails[index];

  return (
    <div style={{ textAlign: 'center', marginTop: '2rem' }}>
      <h1>Arcade Mode</h1>
      <h3>Score: {score}</h3>

      <div className="arcade-box">
        <h2>{email.subject}</h2>
        <div className="email-from">From: {email.sender}</div>
        <div className="arcade-email-body">{email.body}</div>
        <div>
          <button onClick={() => handleGuess(true)}>Phish</button>
          <button onClick={() => handleGuess(false)}>Not Phish</button>
        </div>
        {feedback && <div className="arcade-feedback">{feedback}</div>}
      </div>
    </div>
  );
};

export default ArcadeMode;
