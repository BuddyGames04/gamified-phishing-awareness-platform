const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Login failed');

  const data = await res.json();
  localStorage.setItem('authToken', data.token);
  localStorage.setItem('username', data.username);
  return data;
}

export async function register(username: string, password: string) {
  const res = await fetch(`${API_BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Registration failed');

  const data = await res.json();
  localStorage.setItem('authToken', data.token);
  localStorage.setItem('username', data.username);
  return data;
}

export function authFetch(url: string, options: any = {}) {
  const token = localStorage.getItem('authToken');

  const headers: any = {
    ...(options.headers || {}),
  };

  if (!(options.method === 'GET')) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  return fetch(url, {
    ...options,
    headers,
  });
}
