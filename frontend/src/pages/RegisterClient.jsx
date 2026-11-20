import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { registerClient } from '../api/auth'
import AuthShell from '../components/AuthShell.jsx'
import FormField from '../components/FormField.jsx'
import PasswordStrength from '../components/PasswordStrength.jsx'
import { parseApiError } from '../utils/forms'
import {
  validateConfirm, validateEmail, validateFullName, validatePassword, validatePhone,
} from '../utils/validators'

const INITIAL = {
  full_name: '', email: '', phone: '', password: '', password_confirm: '',
  preferred_language: 'en', accept_terms: false,
}
const FIELDS = Object.keys(INITIAL)

function validate(v) {
  const e = {
    full_name: validateFullName(v.full_name),
    email: validateEmail(v.email),
    phone: validatePhone(v.phone, { required: false }),
    password: validatePassword(v.password),
    password_confirm: validateConfirm(v.password, v.password_confirm),
    accept_terms: v.accept_terms ? '' : 'Accept the terms to continue.',
  }
  return Object.fromEntries(Object.entries(e).filter(([, msg]) => msg))
}

export default function RegisterClient() {
  const [values, setValues] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [general, setGeneral] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState(null)
  const [focusTick, setFocusTick] = useState(0)
  const formRef = useRef(null)

  // Move focus to the first invalid field - only after a failed submit, never while typing.
  useEffect(() => {
    if (focusTick) formRef.current?.querySelector('[aria-invalid="true"]')?.focus()
  }, [focusTick])

  function onChange(e) {
    const { name, type, value, checked } = e.target
    setValues((v) => ({ ...v, [name]: type === 'checkbox' ? checked : value }))
    setErrors((prev) => {
      if (!prev[name]) return prev
      const { [name]: _removed, ...rest } = prev
      return rest
    })
  }

  async function onSubmit(e) {
    e.preventDefault()
    setGeneral('')
    const found = validate(values)
    if (Object.keys(found).length) {
      setErrors(found)
      setFocusTick((t) => t + 1)
      return
    }
    setSubmitting(true)
    try {
      const payload = {
        ...values,
        full_name: values.full_name.trim(),
        email: values.email.trim(),
        phone: values.phone.trim() || undefined,
      }
      setCreated(await registerClient(payload))
    } catch (err) {
      const parsed = parseApiError(err, FIELDS)
      setErrors(parsed.fields)
      setGeneral(parsed.general)
      setFocusTick((t) => t + 1)
    } finally {
      setSubmitting(false)
    }
  }

  if (created) {
    return (
      <AuthShell subtitle="CLIENT ACCOUNT">
        <div className="done">
          <div className="done-mark" aria-hidden="true">✓</div>
          <h2>Account created</h2>
          <p>Welcome, {created.full_name}. You can now log in to find and book a verified advocate.</p>
          <Link to="/login" className="btn">Go to log in</Link>
        </div>
      </AuthShell>
    )
  }

  return (
    <AuthShell subtitle="CLIENT ACCOUNT" backTo="/register" backLabel="← Choose a different account type">
      <h2 className="rg">Create your account</h2>
      <small>Find verified advocates and book consultations.</small>

      <form ref={formRef} onSubmit={onSubmit} noValidate>
        <FormField id="full_name" label="Full name" placeholder="e.g. Ahnaf Shahriar" autoComplete="name"
          value={values.full_name} onChange={onChange} error={errors.full_name} />
        <FormField id="email" label="Email address" type="email" placeholder="you@example.com" autoComplete="email"
          value={values.email} onChange={onChange} error={errors.email} />
        <FormField id="phone" label="Mobile number (optional)" type="tel" placeholder="+880 1712-345678" autoComplete="tel"
          hint="Used for appointment reminders." value={values.phone} onChange={onChange} error={errors.phone} />
        <FormField id="password" label="Password" type="password" autoComplete="new-password"
          value={values.password} onChange={onChange} error={errors.password}
          hint="At least 8 characters with upper and lower case letters, a number and a special character." />
        <PasswordStrength password={values.password} />
        <FormField id="password_confirm" label="Confirm password" type="password" autoComplete="new-password"
          value={values.password_confirm} onChange={onChange} error={errors.password_confirm} />
        <FormField id="preferred_language" label="Preferred language" as="select"
          value={values.preferred_language} onChange={onChange} error={errors.preferred_language}>
          <option value="en">English</option>
          <option value="bn">বাংলা</option>
        </FormField>

        <div className="ck">
          <input id="accept_terms" name="accept_terms" type="checkbox" checked={values.accept_terms} onChange={onChange}
            aria-invalid={errors.accept_terms ? 'true' : undefined}
            aria-describedby={errors.accept_terms ? 'accept_terms-error' : undefined} />
          <label htmlFor="accept_terms">I agree to the LawAid terms of service and privacy policy.</label>
        </div>
        {errors.accept_terms && <div className="fe" id="accept_terms-error" role="alert">{errors.accept_terms}</div>}

        {general && <div className="alert" role="alert">{general}</div>}
        <button type="submit" className="btn" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>

      <hr />
      <p className="foot">Already registered with LawAid? <Link to="/login">Log in</Link></p>
    </AuthShell>
  )
}
