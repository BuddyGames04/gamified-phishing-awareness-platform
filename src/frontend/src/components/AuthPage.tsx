import React, { useState } from 'react';
import '../styles/MenuScreens.css';
import { register, login } from '../api/auth';

interface AuthPageProps {
  onAuthSuccess: (username: string) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const data = isLogin
        ? await login(username, password)
        : await register(username, password);

      localStorage.setItem('authToken', data.token);
      localStorage.setItem('username', data.username);
      onAuthSuccess(data.username);
    } catch (err: any) {
      setError(err?.message || 'Authentication failed');
      console.error(err);
    }
  };

  return (
    <div className="screen-shell">
      <div className="screen-card" style={{ width: 'min(520px, 96vw)' }}>
        <div className="screen-header" style={{ alignItems: 'center' }}>
          <div className="brand">
            <div className="brand-badge">PA</div>
            <div>
              <h1 className="screen-title" style={{ marginBottom: 2 }}>
                {isLogin ? 'Welcome back' : 'Create your account'}
              </h1>
              <p className="screen-subtitle" style={{ marginTop: 0 }}>
                {isLogin
                  ? 'Log in to continue your training.'
                  : 'Register to start tracking your metrics.'}
              </p>
            </div>
          </div>

          <button
            className="ms-btn ms-btn-ghost"
            onClick={() => setIsLogin((v) => !v)}
            title={isLogin ? 'Switch to register' : 'Switch to login'}
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </div>

        <div className="screen-body">
          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-label">
              Username
              <input
                className="auth-input"
                placeholder="e.g. Luke"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </label>

            <label className="auth-label">
              Password
              <input
                className="auth-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={isLogin ? 'current-password' : 'new-password'}
              />
            </label>

            {error && <div className="auth-error">{error}</div>}

            <button className="auth-submit" type="submit">
              {isLogin ? 'Login' : 'Create account'}
            </button>

            <div className="auth-footnote">
              {isLogin ? (
                <>
                  No account yet?{' '}
                  <button
                    type="button"
                    className="auth-link"
                    onClick={() => setIsLogin(false)}
                  >
                    Register
                  </button>
                </>
              ) : (
                <>
                  Already registered?{' '}
                  <button
                    type="button"
                    className="auth-link"
                    onClick={() => setIsLogin(true)}
                  >
                    Login
                  </button>
                </>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
