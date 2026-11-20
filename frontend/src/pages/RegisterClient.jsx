import React, { useState } from 'react';
import { User, Mail, Phone, Lock, Home, AlertCircle, CheckCircle2 } from 'lucide-react';
import AuthShell from '../components/AuthShell';
import FormField from '../components/FormField';
import PasswordStrength from '../components/PasswordStrength';
import { registerClient } from '../api/auth';
import { validateBdPhone, normalizeBdPhone } from '../utils/validators';
import { extractErrorMessage } from '../utils/forms';

export default function RegisterClient({ onRegisterSuccess, onNavigate }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    address: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};

    if (!formData.full_name.trim()) newErrors.full_name = 'Full name is required.';
    if (!formData.email.trim()) newErrors.email = 'Email address is required.';
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    const phoneError = validateBdPhone(formData.phone);
    if (phoneError) newErrors.phone = phoneError;

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    setServerError(null);

    try {
      await registerClient({
        ...formData,
        phone: normalizeBdPhone(formData.phone),
      });
      setSuccess(true);
    } catch (err) {
      setServerError(extractErrorMessage(err.data, 'Registration failed. Please check your information.'));
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <AuthShell title="Registration Complete" subtitle="Your client account has been created">
        <div style={{ textAlign: 'center', padding: '1rem 0' }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              backgroundColor: '#ecfdf5',
              color: '#059669',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
            }}
          >
            <CheckCircle2 size={36} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
            Account Created Successfully
          </h3>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '2rem' }}>
            Welcome to LawAid! You can now sign in to connect with verified advocates and receive judicial assistance.
          </p>
          <button
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem' }}
            onClick={() => onNavigate('login')}
          >
            Proceed to Sign In
          </button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Create Client Account"
      subtitle="Register to find verified advocates and access legal aid"
      badgeIcon={User}
    >
      {serverError && (
        <div className="alert alert-danger">
          <AlertCircle size={18} />
          <span>{serverError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <FormField label="Full Name" id="full_name" error={errors.full_name} required>
          <input
            id="full_name"
            name="full_name"
            type="text"
            className={`form-control ${errors.full_name ? 'is-invalid' : ''}`}
            placeholder="e.g. Rahim Ahmed"
            value={formData.full_name}
            onChange={handleChange}
            required
          />
        </FormField>

        <FormField label="Email Address" id="email" error={errors.email} required>
          <input
            id="email"
            name="email"
            type="email"
            className={`form-control ${errors.email ? 'is-invalid' : ''}`}
            placeholder="rahim@example.com"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </FormField>

        <FormField
          label="Phone Number (BD Mobile)"
          id="phone"
          error={errors.phone}
          helpText="Format: +8801XXXXXXXXX or 01XXXXXXXXX"
          required
        >
          <input
            id="phone"
            name="phone"
            type="tel"
            className={`form-control ${errors.phone ? 'is-invalid' : ''}`}
            placeholder="+8801712345678"
            value={formData.phone}
            onChange={handleChange}
            required
          />
        </FormField>

        <FormField label="Password" id="password" error={errors.password} required>
          <input
            id="password"
            name="password"
            type="password"
            className={`form-control ${errors.password ? 'is-invalid' : ''}`}
            placeholder="Minimum 6 characters"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <PasswordStrength password={formData.password} />
        </FormField>

        <FormField label="Residential Address" id="address" helpText="Optional for contact">
          <textarea
            id="address"
            name="address"
            rows="2"
            className="form-control"
            placeholder="House, Road, Area, District"
            value={formData.address}
            onChange={handleChange}
          />
        </FormField>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '0.75rem', padding: '0.75rem' }}
          disabled={loading}
        >
          {loading ? <div className="spinner" /> : <span>Complete Registration</span>}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: '#64748b' }}>
        Already have an account?{' '}
        <a
          href="#login"
          onClick={(e) => {
            e.preventDefault();
            onNavigate('login');
          }}
          style={{ fontWeight: 600 }}
        >
          Sign In
        </a>
      </div>
    </AuthShell>
  );
}
