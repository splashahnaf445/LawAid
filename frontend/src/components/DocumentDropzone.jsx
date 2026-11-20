import React, { useRef, useState } from 'react';
import { Upload, FileText, CheckCircle2, X, Lock, AlertCircle } from 'lucide-react';
import { formatFileSize } from '../utils/forms';
import { validateDocumentFile } from '../utils/validators';

export default function DocumentDropzone({
  title,
  subtitle,
  docType,
  file,
  onFileSelect,
  onFileRemove,
  error,
  required = true,
}) {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [internalError, setInternalError] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const processFile = (selectedFile) => {
    if (!selectedFile) return;
    const validationError = validateDocumentFile(selectedFile, title);
    if (validationError) {
      setInternalError(validationError);
      return;
    }
    setInternalError(null);
    onFileSelect(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const triggerInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const activeError = error || internalError;

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
        style={{ display: 'none' }}
        onChange={handleInputChange}
      />

      <div
        className={`dropzone-box ${isDragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={file ? undefined : triggerInput}
      >
        {!file ? (
          <>
            <div className="dropzone-icon">
              <Upload size={20} />
            </div>
            <div className="dropzone-title">
              {title} {required && <span style={{ color: '#ef4444' }}>*</span>}
            </div>
            <div className="dropzone-desc">{subtitle || 'PDF, JPG, or PNG (Max 15MB)'}</div>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="btn btn-secondary btn-sm" style={{ pointerEvents: 'none' }}>
                Browse Files
              </span>
            </div>
          </>
        ) : (
          <div className="file-preview">
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '10px',
                backgroundColor: '#ecfdf5',
                color: '#059669',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileText size={22} />
            </div>
            <div className="file-preview-name" title={file.name}>
              {file.name}
            </div>
            <div className="file-preview-size">{formatFileSize(file.size)}</div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
              <button
                type="button"
                className="file-remove-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setInternalError(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                  onFileRemove();
                }}
              >
                <X size={14} /> Remove
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={(e) => {
                  e.stopPropagation();
                  triggerInput();
                }}
              >
                Change
              </button>
            </div>
          </div>
        )}

        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '3px',
            fontSize: '0.68rem',
            color: '#059669',
            fontWeight: 600,
          }}
          title="Encrypted with Fernet AES-128-CBC + HMAC on ingest (NFR-4)"
        >
          <Lock size={10} />
          AES Encrypted
        </div>
      </div>

      {activeError && (
        <div className="form-error" style={{ marginTop: '0.4rem' }}>
          <AlertCircle size={14} />
          <span>{activeError}</span>
        </div>
      )}
    </div>
  );
}
