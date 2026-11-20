import React from 'react';

// Ahnaf (SYS-21/22): labelled form group used by his Login page. Kept as FormGroup because
// FormField.jsx is Usama's component (different props) used by the registration pages.
import { AlertCircle } from 'lucide-react';

export default function FormGroup({
  label,
  id,
  error,
  helpText,
  required = false,
  children,
  className = '',
}) {
  return (
    <div className={`form-group ${className}`}>
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      {children}
      {helpText && !error && <div className="form-text">{helpText}</div>}
      {error && (
        <div className="form-error" role="alert">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
