import React, { useState } from 'react';
import { LogIn, Lock, Mail, AlertCircle, ShieldCheck, UserCheck } from 'lucide-react';
import AuthShell from '../components/AuthShell';
import FormField from '../components/FormField';
import { login } from '../api/auth';
import { extractErrorMessage } from '../utils/forms';

export default function Login({ onLoginSuccess, onNavigate }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await login(email, password);
      if (onLoginSuccess) {
        onLoginSuccess(response.user);
      }
    } catch (err) {
      setError(extractErrorMessage(err.data, 'Invalid email or password.'));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError(null);
  };

  return (
    <AuthShell
      title="Welcome Back"
      subtitle="Sign in to your LawAid account"
      badgeIcon={LogIn}
    >
      {error && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <FormField label="Email Address" id="email" required>
          <div style={{ position: 'relative' }}>
            <input
              id="email"
              type="email"
              className="form-control"
              placeholder="advocate@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </FormField>

        <FormField label="Password" id="password" required>
          <input
            id="password"
            type="password"
            className="form-control"
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormField>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '0.75rem', padding: '0.75rem' }}
          disabled={loading}
        >
          {loading ? (
            <div className="spinner" />
          ) : (
            <>
              <LogIn size={18} />
              <span>Sign In</span>
            </>
          )}
        </button>
      </form>

      {/* Demo Credentials Section for Academic Evaluation */}
      <div className="demo-accounts">
        <div className="demo-title">Test Demo Accounts (Click to Fill)</div>
        <div className="demo-buttons-grid">
          <button
            type="button"
            className="btn-demo"
            onClick={() => handleDemoFill('admin@lawaid.gov.bd', 'AdminPass123!')}
          >
            <strong>Platform Admin</strong>
            <span className="role-tag">admin@lawaid.gov.bd</span>
          </button>

          <button
            type="button"
            className="btn-demo"
            onClick={() => handleDemoFill('tariq.rahman@lawyer.lawaid.com', 'LawyerPass123!')}
          >
            <strong>Verified Lawyer</strong>
            <span className="role-tag">tariq.rahman@lawyer.lawaid.com</span>
          </button>

          <button
            type="button"
            className="btn-demo"
            onClick={() => handleDemoFill('sumaiya.akter@lawyer.lawaid.com', 'LawyerPass123!')}
          >
            <strong>Pending Lawyer</strong>
            <span className="role-tag">sumaiya.akter@... (Pending)</span>
          </button>

          <button
            type="button"
            className="btn-demo"
            onClick={() => handleDemoFill('rahim.ahmed@example.com', 'ClientPass123!')}
          >
            <strong>Standard Client</strong>
            <span className="role-tag">rahim.ahmed@example.com</span>
          </button>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: '#64748b' }}>
        Don't have an account yet?{' '}
        <a
          href="#register"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('role-select');
          }}
          style={{ fontWeight: 600 }}
        >
          Create an Account
        </a>
      </div>
    </AuthShell>
  );
}
