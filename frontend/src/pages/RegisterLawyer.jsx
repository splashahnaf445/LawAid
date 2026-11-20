import React, { useState } from 'react';
import {
  Scale,
  ShieldCheck,
  Lock,
  FileCheck,
  AlertCircle,
  CheckCircle2,
  Building2,
  Briefcase,
  Clock,
  ArrowRight
} from 'lucide-react';
import AuthShell from '../components/AuthShell';
import FormField from '../components/FormField';
import DocumentDropzone from '../components/DocumentDropzone';
import PasswordStrength from '../components/PasswordStrength';
import { registerLawyer } from '../api/auth';
import {
  validateBdPhone,
  normalizeBdPhone,
  validateBarCouncilSanad,
  validateDocumentFile
} from '../utils/validators';
import { extractErrorMessage } from '../utils/forms';

export default function RegisterLawyer({ onNavigate }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    bar_council_sanad_number: '',
    primary_court: 'Supreme Court of Bangladesh, High Court Division',
    district: 'Dhaka',
    chamber_address: '',
    years_of_experience: 3,
    practice_areas: 'Civil Litigation, Constitutional Law',
    bio: '',
  });

  const [nidFile, setNidFile] = useState(null);
  const [barCertFile, setBarCertFile] = useState(null);

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [submissionSuccess, setSubmissionSuccess] = useState(null);

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

    // Basic fields validation
    if (!formData.full_name.trim()) newErrors.full_name = 'Full name is required.';
    if (!formData.email.trim()) newErrors.email = 'Email address is required.';
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    // Phone validation
    const phoneError = validateBdPhone(formData.phone_number);
    if (phoneError) newErrors.phone_number = phoneError;

    // Sanad number validation (FR-2)
    const sanadError = validateBarCouncilSanad(formData.bar_council_sanad_number);
    if (sanadError) newErrors.bar_council_sanad_number = sanadError;

    // Document file validations (FR-2, NFR-4)
    const nidError = validateDocumentFile(nidFile, 'National ID Card');
    if (nidError) newErrors.nid_card = nidError;

    const certError = validateDocumentFile(barCertFile, 'Bar Council Certificate');
    if (certError) newErrors.bar_council_certificate = certError;

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      // Scroll to top of form
      window.scrollTo({ top: 100, behavior: 'smooth' });
      return;
    }

    setLoading(true);
    setServerError(null);

    try {
      const payload = new FormData();
      payload.append('full_name', formData.full_name);
      payload.append('email', formData.email);
      payload.append('phone_number', normalizeBdPhone(formData.phone_number));
      payload.append('password', formData.password);
      payload.append('bar_council_sanad_number', formData.bar_council_sanad_number.trim());
      payload.append('primary_court', formData.primary_court);
      payload.append('district', formData.district);
      payload.append('chamber_address', formData.chamber_address);
      payload.append('years_of_experience', formData.years_of_experience);
      payload.append('practice_areas', formData.practice_areas);
      payload.append('bio', formData.bio);
      payload.append('nid_card', nidFile);
      payload.append('bar_council_certificate', barCertFile);

      const response = await registerLawyer(payload);
      setSubmissionSuccess(response);
    } catch (err) {
      setServerError(
        extractErrorMessage(
          err.data,
          'Registration submission failed. Please verify your files and information.'
        )
      );
    } finally {
      setLoading(false);
    }
  };

  // Success view with clear verification status (SRS FR-2, FR-3)
  if (submissionSuccess) {
    return (
      <AuthShell
        title="Application Submitted & Encrypted"
        subtitle="Verification Queue Confirmation"
        badgeIcon={ShieldCheck}
        wide
      >
        <div style={{ textAlign: 'center', padding: '1rem 0' }}>
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              backgroundColor: '#ecfdf5',
              color: '#059669',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              border: '2px solid #a7f3d0',
            }}
          >
            <Lock size={36} />
          </div>

          <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.75rem' }}>
            Verification Documents Encrypted & Queued
          </h3>

          <div
            style={{
              maxWidth: '560px',
              margin: '0 auto 1.75rem',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.25rem',
              textAlign: 'left',
              fontSize: '0.875rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid #e2e8f0' }}>
              <span style={{ color: '#64748b' }}>Bar Council Sanad:</span>
              <strong style={{ fontFamily: 'monospace', color: '#0f172a' }}>{submissionSuccess.bar_council_no}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #e2e8f0' }}>
              <span style={{ color: '#64748b' }}>Verification Status:</span>
              <span className="badge badge-warning">Pending Admin Review</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #e2e8f0' }}>
              <span style={{ color: '#64748b' }}>Document Encryption:</span>
              <span className="badge badge-success">AES-128-CBC + HMAC-SHA256 (At Rest)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '0.5rem' }}>
              <span style={{ color: '#64748b' }}>Public Search Visibility:</span>
              <span style={{ color: '#b45309', fontWeight: 600 }}>Hidden until approved (FR-3)</span>
            </div>
          </div>

          <div className="alert alert-info" style={{ textAlign: 'left', maxWidth: '560px', margin: '0 auto 2rem' }}>
            <FileCheck size={20} style={{ flexShrink: 0 }} />
            <div>
              <strong>What happens next?</strong>
              <p style={{ marginTop: '0.25rem', fontSize: '0.825rem', lineHeight: 1.5 }}>
                A platform compliance administrator will inspect your encrypted Bar Council credentials against official registers.
                Upon approval, your profile will be unlocked for public client searches with the verified advocate badge.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
            <button
              className="btn btn-primary"
              style={{ padding: '0.75rem 2rem' }}
              onClick={() => onNavigate('login')}
            >
              Sign In to Your Dashboard
            </button>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.75rem 1.5rem' }}
              onClick={() => onNavigate('lawyers')}
            >
              Explore Lawyer Directory
            </button>
          </div>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Lawyer & Advocate Registration"
      subtitle="Register with your Bangladesh Bar Council Sanad credentials"
      badgeIcon={Scale}
      wide
    >
      {/* Security Assurance Banner (NFR-4) */}
      <div className="security-callout">
        <div className="security-callout-icon">
          <Lock size={20} />
        </div>
        <div className="security-callout-content">
          <h4>End-to-End Encrypted Verification Ingestion (SRS FR-2, NFR-4)</h4>
          <p>
            Your National ID card and Bar Council Sanad certificate are encrypted with Fernet AES-128-CBC and
            HMAC-SHA256 on ingestion. Documents are never stored in plaintext and are decryptable only by
            authorized platform compliance officers during verification.
          </p>
        </div>
      </div>

      {serverError && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} />
          <span>{serverError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {/* Personal Info */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              1. Advocate Information
            </h4>

            <FormField label="Full Name (As on Bar Certificate)" id="full_name" error={errors.full_name} required>
              <input
                id="full_name"
                name="full_name"
                type="text"
                className={`form-control ${errors.full_name ? 'is-invalid' : ''}`}
                placeholder="Advocate Tariq Rahman"
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
                placeholder="advocate.rahman@lawyer.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </FormField>

            <FormField
              label="Phone Number (BD Mobile)"
              id="phone_number"
              error={errors.phone_number}
              helpText="e.g. +8801712345678 or 01712345678"
              required
            >
              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                className={`form-control ${errors.phone_number ? 'is-invalid' : ''}`}
                placeholder="+8801712345678"
                value={formData.phone_number}
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
                placeholder="••••••••••••"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <PasswordStrength password={formData.password} />
            </FormField>
          </div>

          {/* Practice & Bar Credentials */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              2. Bar Council & Jurisdiction
            </h4>

            <FormField
              label="Bar Council Sanad Number"
              id="bar_council_sanad_number"
              error={errors.bar_council_sanad_number}
              helpText="Format: <SanadNumber>/<EnrollmentYear> (e.g. 14205/2018)"
              required
            >
              <input
                id="bar_council_sanad_number"
                name="bar_council_sanad_number"
                type="text"
                className={`form-control ${errors.bar_council_sanad_number ? 'is-invalid' : ''}`}
                placeholder="14205/2018"
                value={formData.bar_council_sanad_number}
                onChange={handleChange}
                required
              />
            </FormField>

            <FormField label="Primary Court of Practice" id="primary_court" required>
              <select
                id="primary_court"
                name="primary_court"
                className="form-control"
                value={formData.primary_court}
                onChange={handleChange}
              >
                <option value="Supreme Court of Bangladesh, High Court Division">
                  Supreme Court of Bangladesh, High Court Division
                </option>
                <option value="Supreme Court of Bangladesh, Appellate Division">
                  Supreme Court of Bangladesh, Appellate Division
                </option>
                <option value="Dhaka District & Sessions Judge Court">
                  Dhaka District & Sessions Judge Court
                </option>
                <option value="Chittagong District & Sessions Judge Court">
                  Chittagong District & Sessions Judge Court
                </option>
                <option value="Sylhet District & Sessions Judge Court">
                  Sylhet District & Sessions Judge Court
                </option>
              </select>
            </FormField>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <FormField label="District" id="district" required>
                <input
                  id="district"
                  name="district"
                  type="text"
                  className="form-control"
                  placeholder="Dhaka"
                  value={formData.district}
                  onChange={handleChange}
                  required
                />
              </FormField>

              <FormField label="Years of Experience" id="years_of_experience" required>
                <input
                  id="years_of_experience"
                  name="years_of_experience"
                  type="number"
                  min="0"
                  max="60"
                  className="form-control"
                  value={formData.years_of_experience}
                  onChange={handleChange}
                  required
                />
              </FormField>
            </div>

            <FormField label="Practice Areas" id="practice_areas" helpText="Comma-separated">
              <input
                id="practice_areas"
                name="practice_areas"
                type="text"
                className="form-control"
                placeholder="Civil Litigation, Criminal Defense, Family Law"
                value={formData.practice_areas}
                onChange={handleChange}
              />
            </FormField>
          </div>
        </div>

        {/* Section 3: Encrypted Documents Upload (FR-2, NFR-4) */}
        <div style={{ marginTop: '1.75rem' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>3. Verification Documents (Encrypted at Rest)</span>
            <Lock size={15} color="#0d9488" />
          </h4>
          <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '1rem' }}>
            Upload high-resolution scans or photos. Maximum size 15MB per file (PDF, JPG, or PNG).
          </p>

          <div className="document-upload-grid">
            <DocumentDropzone
              title="National ID Card (NID)"
              subtitle="Front & back copy (PDF, JPG, PNG)"
              docType="nid"
              file={nidFile}
              onFileSelect={(f) => {
                setNidFile(f);
                setErrors((prev) => ({ ...prev, nid_card: null }));
              }}
              onFileRemove={() => setNidFile(null)}
              error={errors.nid_card}
              required
            />

            <DocumentDropzone
              title="Bar Council Sanad Certificate"
              subtitle="Official Bar Council Certificate (PDF, JPG, PNG)"
              docType="bar_certificate"
              file={barCertFile}
              onFileSelect={(f) => {
                setBarCertFile(f);
                setErrors((prev) => ({ ...prev, bar_council_certificate: null }));
              }}
              onFileRemove={() => setBarCertFile(null)}
              error={errors.bar_council_certificate}
              required
            />
          </div>
        </div>

        <FormField label="Chamber Address & Brief Professional Bio" id="chamber_address">
          <textarea
            id="chamber_address"
            name="chamber_address"
            rows="2"
            className="form-control"
            placeholder="Room 402, Supreme Court Bar Association Building, Ramna, Dhaka"
            value={formData.chamber_address}
            onChange={handleChange}
          />
        </FormField>

        {/* Compliance agreement */}
        <div style={{ background: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.5rem', fontSize: '0.8rem', color: '#64748b' }}>
          By submitting this registration, I declare under penalty of law that I am an enrolled advocate with the Bangladesh
          Bar Council. I understand that my profile will remain hidden from client searches until my uploaded credentials are
          independently verified and approved by LawAid compliance officers (SRS FR-3).
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', padding: '0.85rem', fontSize: '1rem' }}
          disabled={loading}
        >
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div className="spinner" />
              <span>Encrypting Documents & Registering...</span>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={20} />
              <span>Submit for Bar Council Verification</span>
            </div>
          )}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: '#64748b' }}>
        Already registered?{' '}
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
