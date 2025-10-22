import React, { useEffect, useState } from 'react';
import { Email, fetchEmails, submitResult } from '../api';

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
      <div
        style={{
          margin: '1rem auto',
          maxWidth: '600px',
          border: '1px solid #ccc',
          padding: '1rem',
        }}
      >
        <h2>{email.subject}</h2>
        <p>
          <em>From:</em> {email.sender}
        </p>
        <p>{email.body}</p>
        <div style={{ marginTop: '1rem' }}>
          <button onClick={() => handleGuess(true)}>Phish</button>
          <button onClick={() => handleGuess(false)}>Not Phish</button>
        </div>
        {feedback && <p style={{ fontSize: '1.2em' }}>{feedback}</p>}
      </div>
    </div>
  );
};

export default ArcadeMode;
