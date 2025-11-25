import React, { useState } from 'react';
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
    try {
      const data = isLogin
        ? await login(username, password)
        : await register(username, password);
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('username', data.username);
      onAuthSuccess(data.username);
      console.log("Login succeeded, data:", data);
    } catch (err) {
      setError('Authentication failed');
      console.error(err);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '3rem' }}>
      <h1>{isLogin ? 'Login' : 'Register'}</h1>
      <form onSubmit={handleSubmit}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <br />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <br />
        <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
      </form>
      <button onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? 'Need an account? Register' : 'Already have one? Login'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default AuthPage;
