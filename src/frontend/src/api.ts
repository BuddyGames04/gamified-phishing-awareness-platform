import { authFetch } from './api/auth';

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

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export async function fetchEmails(): Promise<Email[]> {
  const response = await authFetch(`${API_BASE}/emails/`);
  if (!response.ok) throw new Error('Failed to fetch emails');
  return response.json();
}

export async function submitResult(
  userId: string,
  isCorrect: boolean
): Promise<UserProgress> {
  const response = await authFetch(`${API_BASE}/submit/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify({ user_id: userId, is_correct: isCorrect }),
  });
  if (!response.ok) throw new Error('Failed to submit result');
  return response.json();
}
