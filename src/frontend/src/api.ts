export interface Email {
  id: number;
  sender: string;
  subject: string;
  body: string;
  is_phish: boolean;
  difficulty: number;
  category?: string;
}

export interface UserProgress {
  user_id: string;
  score: number;
  correct: number;
  incorrect: number;
  total_attempts: number;
  last_updated: string;
}

const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchEmails(): Promise<Email[]> {
  const response = await fetch(`${API_BASE}/emails/`);
  if (!response.ok) throw new Error("Failed to fetch emails");
  return response.json();
}

export async function submitResult(userId: string, isCorrect: boolean): Promise<UserProgress> {
  const response = await fetch(`${API_BASE}/submit/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, is_correct: isCorrect }),
  });
  if (!response.ok) throw new Error("Failed to submit result");
  return response.json();
}
