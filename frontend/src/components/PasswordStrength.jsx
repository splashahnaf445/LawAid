import React from 'react';
import { Check, X } from 'lucide-react';

export default function PasswordStrength({ password = '' }) {
  if (!password) return null;

  const checks = [
    { label: 'At least 8 characters', valid: password.length >= 8 },
    { label: 'Contains a number', valid: /\d/.test(password) },
    { label: 'Contains a letter', valid: /[a-zA-Z]/.test(password) },
  ];

  const score = checks.filter((c) => c.valid).length;
  const strengthColors = ['#ef4444', '#f59e0b', '#10b981'];
  const strengthLabels = ['Weak', 'Moderate', 'Strong'];

  return (
    <div style={{ marginTop: '0.4rem', marginBottom: '0.75rem' }}>
      <div style={{ display: 'flex', gap: '4px', height: '4px', marginBottom: '6px' }}>
        {[0, 1, 2].map((idx) => (
          <div
            key={idx}
            style={{
              flex: 1,
              backgroundColor: idx < score ? strengthColors[score - 1] : '#e2e8f0',
              borderRadius: '2px',
              transition: 'background-color 0.2s',
            }}
          />
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
        <span style={{ color: strengthColors[Math.max(0, score - 1)], fontWeight: 600 }}>
          {strengthLabels[Math.max(0, score - 1)]}
        </span>
        <div style={{ display: 'flex', gap: '8px', color: '#64748b' }}>
          {checks.map((check, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              {check.valid ? (
                <Check size={11} color="#10b981" />
              ) : (
                <X size={11} color="#94a3b8" />
              )}
              {check.label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
