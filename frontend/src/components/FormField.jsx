/**
 * Label + control + hint + inline error, wired for screen readers
 * (aria-invalid / aria-describedby). `as` can be 'input' (default), 'select' or 'textarea';
 * select options are passed as children.
 */
export default function FormField({ id, label, hint, error, as: Control = 'input', children, ...controlProps }) {
  const hintId = hint ? `${id}-hint` : undefined
  const errorId = error ? `${id}-error` : undefined
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined
  return (
    <div className="ff">
      <label className="k" htmlFor={id}>{label}</label>
      <Control
        id={id}
        name={id}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        {...controlProps}
      >
        {children}
      </Control>
      {hint && <div className="fg" id={hintId}>{hint}</div>}
      {error && <div className="fe" id={errorId} role="alert">{error}</div>}
    </div>
  )
}
