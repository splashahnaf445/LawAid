import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function FormField({
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
