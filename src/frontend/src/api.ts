import { authFetch } from './api/auth';

export interface Email {
  id: number;
  sender_name: string;
  sender_email: string;
  subject: string;
  body: string;
  is_phish: boolean;
  difficulty: number;
  category?: string;
  links?: string[];
  attachments?: string[];
}

export interface UserProgress {
  user_id: string;
  score: number;
  correct: number;
  incorrect: number;
  total_attempts: number;
  last_updated: string;
}

export interface InteractionEvent {
  id: number;
  user_id: string;
  email: number; // (backend returns FK as id)
  event_type: string;
  value?: string | null;
  created_at: string;
}

export interface Scenario {
  id: number;
  company_name: string;
  sector: string;
  role_title: string;
  department_name: string;
  line_manager_name: string;
  responsibilities: string[];
  intro_text: string;
}

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export async function fetchEmails(params?: {
  mode?: 'arcade' | 'simulation';
  scenario_id?: number;
}): Promise<Email[]> {
  const qs = new URLSearchParams();
  if (params?.mode) qs.set('mode', params.mode);
  if (params?.scenario_id) qs.set('scenario_id', String(params.scenario_id));

  const url = `${API_BASE}/emails/${qs.toString() ? `?${qs.toString()}` : ''}`;

  const response = await authFetch(url);
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

export async function submitInteraction(
  userId: string,
  emailId: number,
  eventType: string,
  value?: string
): Promise<InteractionEvent> {
  const response = await authFetch(`${API_BASE}/interaction/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify({
      user_id: userId,
      email_id: emailId,
      event_type: eventType,
      value: value ?? null,
    }),
  });

  if (!response.ok) throw new Error('Failed to submit interaction');
  return response.json();
}

export async function fetchScenarios(): Promise<Scenario[]> {
  const response = await authFetch(`${API_BASE}/scenarios/`);
  if (!response.ok) throw new Error('Failed to fetch scenarios');
  return response.json();
}

