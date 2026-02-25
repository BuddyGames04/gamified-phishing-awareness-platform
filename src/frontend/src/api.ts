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
  min_difficulty?: number;
  max_difficulty?: number;
  limit?: number;
  level?: number;
  wave?: boolean;
}): Promise<Email[]> {
  const qs = new URLSearchParams();
  if (params?.mode) qs.set('mode', params.mode);
  if (params?.scenario_id) qs.set('scenario_id', String(params.scenario_id));
  if (params?.min_difficulty) qs.set('min_difficulty', String(params.min_difficulty));
  if (params?.max_difficulty) qs.set('max_difficulty', String(params.max_difficulty));
  if (params?.limit) qs.set('limit', String(params.limit));
  if (params?.level) qs.set('level', String(params.level));
  if (params?.wave) qs.set('wave', 'true');

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

export interface LevelRunStartResponse {
  id: number;
  user_id: string;
  mode: 'arcade' | 'simulation';
  scenario_id?: number | null;
  level_number: number;
  emails_total: number;
  started_at: string;
}

export async function startLevelRun(params: {
  user_id: string;
  mode: 'arcade' | 'simulation';
  scenario_id?: number;
  level_number: number;
  emails_total: number;
}): Promise<LevelRunStartResponse> {
  const response = await authFetch(`${API_BASE}/metrics/level-runs/start/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify(params),
  });

  if (!response.ok) throw new Error('Failed to start level run');
  return response.json();
}

export async function completeLevelRun(
  runId: number,
  params: { correct: number; incorrect: number }
) {
  const response = await authFetch(
    `${API_BASE}/metrics/level-runs/${runId}/complete/`,
    {
      method: 'POST',
      headers: {},
      body: JSON.stringify(params),
    }
  );

  if (!response.ok) throw new Error('Failed to complete level run');
  return response.json();
}

export async function createDecisionEvent(params: {
  user_id: string;
  run_id?: number | null;
  email_id: number;
  decision: 'report_phish' | 'mark_read' | 'mark_safe';
  was_correct: boolean;
}) {
  const response = await authFetch(`${API_BASE}/metrics/decisions/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify(params),
  });

  if (!response.ok) throw new Error('Failed to create decision event');
  return response.json();
}

export type ProfileMetrics = {
  user_id: string;
  overall: {
    total_runs: number;
    total_attempts: number;
    accuracy: number; // 0..1
    decision_events: number;
    pct_link_click_before_decision: number; // 0..100
    pct_attachment_open_before_decision: number; // 0..100
  };
  recent_runs: Array<{
    id?: number;
    mode?: string;
    scenario_id?: number | null;
    level_number?: number;
    emails_total?: number;
    correct?: number;
    incorrect?: number;
    started_at?: string;
    completed_at?: string | null;
  }>;
  by_level: Array<{
    level_number: number;
    scenario_id?: number | null;
    runs: number;
    correct: number;
    incorrect: number;
    accuracy: number; // 0..1 OR 0..100 depending on backend(check)
    last_played_at?: string | null;
  }>;
  trends: {
    accuracy: Array<{
      date: string;
      accuracy: number; // 0..1 OR 0..100
      risky_action_rate?: number;
    }>;
  };
};

export async function fetchProfileMetrics(userId: string): Promise<ProfileMetrics> {
  const url = `${API_BASE}/profile/metrics/?user_id=${encodeURIComponent(userId)}`;
  const res = await authFetch(url, { method: 'GET' });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Profile metrics failed (${res.status}): ${text}`);
  }

  return res.json();
}

export type ArcadeNextEmail = Email & {
  target_difficulty: number;
  target_difficulty_int: number;
};

export type ArcadeAttemptResponse = {
  was_correct: boolean;
  new_target_difficulty: number;
  accuracy: number; // 0..1
};

export async function fetchArcadeNext(): Promise<ArcadeNextEmail> {
  const res = await authFetch(`${API_BASE}/arcade/next/`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to fetch arcade next email');
  return res.json();
}

export async function postArcadeAttempt(params: {
  email_id: number;
  guess_is_phish: boolean;
  response_time_ms?: number;
}): Promise<ArcadeAttemptResponse> {
  const res = await authFetch(`${API_BASE}/arcade/attempt/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to submit arcade attempt');
  return res.json();
}

export type PvpVisibility = 'unlisted' | 'posted';

export type PvpScenario = {
  id: number;
  name: string;
  company_name: string;
  sector: string;
  role_title: string;
  department_name: string;
  line_manager_name: string;
  responsibilities: string[];
  intro_text: string;
  created_at: string;
};

export type PvpLevel = {
  id: number;
  scenario: PvpScenario;
  title: string;
  briefing: string;
  visibility: PvpVisibility;
  plays: number;
  avg_accuracy: number;
  created_at: string;
};

export type PvpEmail = {
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
  is_wave: boolean;
  sort_order: number;
  created_at: string;
};

// ---- PVP Endpoints ----

export async function fetchPvpPostedLevels(): Promise<PvpLevel[]> {
  const res = await authFetch(`${API_BASE}/pvp/levels/posted/`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to fetch posted PVP levels');
  return res.json();
}

export async function fetchPvpMyLevels(): Promise<PvpLevel[]> {
  const res = await authFetch(`${API_BASE}/pvp/levels/mine/`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to fetch my PVP levels');
  return res.json();
}

export async function fetchPvpMyScenarios(): Promise<PvpScenario[]> {
  const res = await authFetch(`${API_BASE}/pvp/scenarios/mine/`, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to fetch my PVP scenarios');
  return res.json();
}

export async function createPvpScenario(params: {
  name: string;
  company_name: string;
  sector: string;
  role_title: string;
  department_name: string;
  line_manager_name: string;
  responsibilities: string[];
  intro_text: string;
}): Promise<PvpScenario> {
  const res = await authFetch(`${API_BASE}/pvp/scenarios/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create PVP scenario: ${text}`);
  }
  return res.json();
}

export async function createPvpLevel(params: {
  scenario_id: number;
  title: string;
  briefing: string;
  visibility?: PvpVisibility;
}): Promise<PvpLevel> {
  const res = await authFetch(`${API_BASE}/pvp/levels/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create PVP level: ${text}`);
  }
  return res.json();
}

export async function publishPvpLevel(levelId: number): Promise<PvpLevel> {
  const res = await authFetch(`${API_BASE}/pvp/levels/${levelId}/publish/`, {
    method: 'PATCH',
    headers: {},
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to publish PVP level: ${text}`);
  }
  return res.json();
}

export async function deletePvpLevel(levelId: number): Promise<void> {
  const res = await authFetch(`${API_BASE}/pvp/levels/${levelId}/`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to delete PVP level: ${text}`);
  }
}

export async function createPvpEmail(params: {
  level_id: number;
  sender_name: string;
  sender_email: string;
  subject: string;
  body: string;
  is_phish: boolean;
  difficulty: number;
  category?: string | null;
  links?: string[];
  attachments?: string[];
  is_wave: boolean;
  sort_order: number;
}): Promise<PvpEmail> {
  const res = await authFetch(`${API_BASE}/pvp/levels/${params.level_id}/emails/create/`, {
    method: 'POST',
    headers: {},
    body: JSON.stringify({
      sender_name: params.sender_name,
      sender_email: params.sender_email,
      subject: params.subject,
      body: params.body,
      is_phish: params.is_phish,
      difficulty: params.difficulty,
      category: params.category ?? null,
      links: params.links ?? [],
      attachments: params.attachments ?? [],
      is_wave: params.is_wave,
      sort_order: params.sort_order,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create PVP email: ${text}`);
  }
  return res.json();
}

export async function fetchPvpEmails(params: {
  level_id: number;
  limit?: number;
  wave?: boolean;
}): Promise<Email[]> {
  const qs = new URLSearchParams();
  qs.set('level_id', String(params.level_id));
  if (params.limit) qs.set('limit', String(params.limit));
  if (params.wave) qs.set('wave', String(params.wave));

  const url = `${API_BASE}/pvp/play/emails/?${qs.toString()}`;
  const res = await authFetch(url, { method: 'GET' });
  if (!res.ok) throw new Error('Failed to fetch PVP play emails');
  return res.json();
}

export function normaliseEmailPayload(email: any) {
  const tidy = (s: any) => String(s ?? '').trim().replace(/\s+/g, ' ');
  const tidyList = (xs: any) =>
    Array.isArray(xs) ? xs.map((x) => String(x).trim()).filter(Boolean) : [];

  const sender_name = tidy(email.sender_name);
  const sender_email = tidy(email.sender_email).toLowerCase();
  const subject = tidy(email.subject);
  const body = String(email.body ?? '');

  const links = tidyList(email.links);
  const attachments = tidyList(email.attachments).map((f) =>
    //make filenames safe-ish
    f.replace(/\s+/g, '_')
  );

  return {
    ...email,
    sender_name,
    sender_email,
    subject,
    body,
    links,
    attachments,
  };
}