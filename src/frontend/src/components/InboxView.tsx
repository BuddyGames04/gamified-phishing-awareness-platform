import React, { useEffect, useState } from "react";
import { Email, fetchEmails, submitResult } from "../api";

const InboxView: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selected, setSelected] = useState<Email | null>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [score, setScore] = useState(0);

  useEffect(() => {
    const loadEmails = async () => {
      try {
        const data = await fetchEmails();
        setEmails(data);
      } catch (err) {
        console.error("Failed to load emails:", err);
      }
    };
    loadEmails();
  }, []);

  const handleDecision = async (isPhishGuess: boolean) => {
    if (!selected) return;

    const isCorrect = selected.is_phish === isPhishGuess;
    setFeedback(isCorrect ? "Correct" : "Wrong");
    const correct = selected.is_phish === isPhishGuess;

    if (isCorrect) {
    setScore(prev => prev + 1);
    }

    try {
      await submitResult("luke", isCorrect);
    } catch (err) {
      console.error("Error submitting result:", err);
    }

    // Reset after 1.2s
    setTimeout(() => {
      setSelected(null);
      setFeedback("");
    }, 1200);
  };

  return (
    <div style={{ display: "flex", gap: "1rem" }}>
      <h3>Score: {score}</h3>
      {/* Sidebar */}
      <div style={{ width: "250px", borderRight: "1px solid #ccc" }}>
        <h3>Inbox</h3>
        {emails.map((email) => (
          <div
            key={email.id}
            onClick={() => setSelected(email)}
            style={{
              padding: "8px",
              cursor: "pointer",
              background: selected?.id === email.id ? "#eef" : "white",
            }}
          >
            <strong>{email.sender}</strong>
            <div>{email.subject}</div>
          </div>
        ))}
      </div>

      {/* Main email view */}
      <div style={{ flex: 1, padding: "1rem" }}>
        {selected ? (
          <>
            <h2>{selected.subject}</h2>
            <p><em>From:</em> {selected.sender}</p>
            <p>{selected.body}</p>

            <div style={{ marginTop: "1rem" }}>
              <button onClick={() => handleDecision(true)}>Report Phish</button>
              <button onClick={() => handleDecision(false)}>Mark Safe</button>
            </div>

            {feedback && <p style={{ fontSize: "1.2em" }}>{feedback}</p>}
          </>
        ) : (
          <p>Select an email to read</p>
        )}
      </div>
    </div>
  );
};

export default InboxView;
