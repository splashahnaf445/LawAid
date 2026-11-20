import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { listCourts, listPracticeAreas, registerLawyer } from '../api/auth'
import AuthShell from '../components/AuthShell.jsx'
import FormField from '../components/FormField.jsx'
import PasswordStrength from '../components/PasswordStrength.jsx'
import { parseApiError } from '../utils/forms'
import {
  normalizeBarCouncilNo, validateBarCouncilNo, validateConfirm, validateEmail, validateFee,
  validateFullName, validatePassword, validatePhone,
} from '../utils/validators'

const INITIAL = {
  full_name: '', phone: '', email: '', primary_court: '', preferred_language: 'en',
  bar_council_no: '', bar_association: '', practice_areas: [], chamber_address: '',
  password: '', password_confirm: '', consultation_fee: '', two_factor_enabled: true, accept_terms: false,
}

// Which step owns which field - used to jump back when the server rejects something earlier.
const STEP_FIELDS = {
  1: ['full_name', 'phone', 'email', 'primary_court', 'preferred_language'],
  2: ['bar_council_no', 'bar_association', 'practice_areas', 'chamber_address'],
  3: ['password', 'password_confirm', 'consultation_fee', 'two_factor_enabled', 'accept_terms'],
}
const ALL_FIELDS = Object.values(STEP_FIELDS).flat()
const stepOf = (field) => Number(Object.keys(STEP_FIELDS).find((s) => STEP_FIELDS[s].includes(field)))

const BAR_ASSOCIATIONS = [
  'Supreme Court Bar Association',
  'Dhaka Bar Association',
  'Chattogram Bar Association',
]

function validateStep(step, v) {
  const e = {}
  if (step === 1) {
    e.full_name = validateFullName(v.full_name)
    e.phone = validatePhone(v.phone, { required: true })
    e.email = validateEmail(v.email)
    e.primary_court = v.primary_court ? '' : 'Select your primary court.'
  } else if (step === 2) {
    e.bar_council_no = validateBarCouncilNo(v.bar_council_no)
    e.bar_association = v.bar_association.trim() ? '' : 'Select or type your bar association.'
    e.practice_areas = v.practice_areas.length ? '' : 'Select at least one practice area.'
    e.chamber_address = v.chamber_address.trim() ? '' : 'Enter your chamber or office address.'
  } else {
    e.password = validatePassword(v.password)
    e.password_confirm = validateConfirm(v.password, v.password_confirm)
    e.consultation_fee = validateFee(v.consultation_fee)
    e.accept_terms = v.accept_terms ? '' : 'Accept the terms to complete registration.'
  }
  return Object.fromEntries(Object.entries(e).filter(([, msg]) => msg))
}

const STEP_COPY = {
  1: ['Create lawyer account', 'Step 1: Your personal and contact profile'],
  2: ['Professional and Bar verification', 'Step 2: Bangladesh Bar Council and chamber enrollment'],
  3: ['Set security and preferences', 'Step 3 of 3: Secure your chamber portal'],
}

export default function RegisterLawyer() {
  const [step, setStep] = useState(1)
  const [values, setValues] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [general, setGeneral] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState(null)
  const [focusTick, setFocusTick] = useState(0)
  const [ref, setRef] = useState({ courts: [], areas: [], loading: true, failed: false })
  const formRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([listCourts(), listPracticeAreas()])
      .then(([courts, areas]) => { if (!cancelled) setRef({ courts, areas, loading: false, failed: false }) })
      .catch(() => { if (!cancelled) setRef({ courts: [], areas: [], loading: false, failed: true }) })
    return () => { cancelled = true }
  }, [])

  // Focus the first invalid field after a failed Continue/submit - never while typing.
  useEffect(() => {
    if (focusTick) formRef.current?.querySelector('[aria-invalid="true"], [data-invalid="true"]')?.focus()
  }, [focusTick])

  function clearError(name) {
    setErrors((prev) => {
      if (!prev[name]) return prev
      const { [name]: _removed, ...rest } = prev
      return rest
    })
  }

  function onChange(e) {
    const { name, type, value, checked } = e.target
    setValues((v) => ({ ...v, [name]: type === 'checkbox' ? checked : value }))
    clearError(name)
  }

  function toggleArea(id) {
    setValues((v) => ({
      ...v,
      practice_areas: v.practice_areas.includes(id)
        ? v.practice_areas.filter((x) => x !== id)
        : [...v.practice_areas, id],
    }))
    clearError('practice_areas')
  }

  function fail(found, atStep) {
    setErrors(found)
    if (atStep) setStep(atStep)
    setFocusTick((t) => t + 1)
  }

  async function submit() {
    // Re-check every step so nothing reaches the server unvalidated.
    for (const s of [1, 2, 3]) {
      const found = validateStep(s, values)
      if (Object.keys(found).length) return fail(found, s)
    }
    setSubmitting(true)
    try {
      const payload = {
        full_name: values.full_name.trim(),
        phone: values.phone.trim(),
        email: values.email.trim(),
        preferred_language: values.preferred_language,
        primary_court: Number(values.primary_court),
        bar_council_no: normalizeBarCouncilNo(values.bar_council_no),
        bar_association: values.bar_association.trim(),
        practice_areas: values.practice_areas,
        chamber_address: values.chamber_address.trim(),
        password: values.password,
        password_confirm: values.password_confirm,
        consultation_fee: values.consultation_fee.trim() || '0',
        two_factor_enabled: values.two_factor_enabled,
        accept_terms: values.accept_terms,
      }
      setCreated(await registerLawyer(payload))
    } catch (err) {
      const parsed = parseApiError(err, ALL_FIELDS)
      setGeneral(parsed.general)
      // e.g. "email already registered" is a step-1 field even though we submit from step 3
      const steps = Object.keys(parsed.fields).map(stepOf)
      fail(parsed.fields, steps.length ? Math.min(...steps) : null)
    } finally {
      setSubmitting(false)
    }
  }

  function onSubmit(e) {
    e.preventDefault()
    setGeneral('')
    if (step === 3) return submit()
    const found = validateStep(step, values)
    if (Object.keys(found).length) return fail(found)
    setErrors({})
    setStep(step + 1)
  }

  if (created) {
    return (
      <AuthShell subtitle="ADVOCATE & LEGAL COUNSEL">
        <div className="done">
          <div className="done-mark" aria-hidden="true">✓</div>
          <h2>Application received</h2>
          <p>
            Thanks, {created.honorific ? `${created.honorific} ` : ''}{created.full_name}. Your account is pending
            verification. We’ll check your Bar Council number ({created.bar_council_no}) before your profile can accept bookings.
          </p>
          <Link to="/login" className="btn">Go to log in</Link>
        </div>
      </AuthShell>
    )
  }

  const stepClass = (n) => (step > n ? 'd' : step === n ? 'c' : undefined)
  const [title, subtitle] = STEP_COPY[step]

  return (
    <AuthShell subtitle="ADVOCATE & LEGAL COUNSEL" backTo="/register" backLabel="← Choose a different account type">
      <div className="stp" aria-label={`Step ${step} of 3`}>
        <span className={stepClass(1)}><i aria-hidden="true">{step > 1 ? '✓' : '1'}</i>Personal info</span>
        <span className={stepClass(2)}><i aria-hidden="true">{step > 2 ? '✓' : '2'}</i>Bar &amp; practice</span>
        <span className={stepClass(3)}><i aria-hidden="true">3</i>Security</span>
      </div>
      <div className="pb2"><i style={{ width: `${step * 33 + (step === 3 ? 1 : 0)}%` }} /></div>
      <h2 className="rg">{title}</h2>
      <small>{subtitle}</small>

      <form ref={formRef} onSubmit={onSubmit} noValidate>
        {step === 1 && (
          <>
            {ref.failed && (
              <div className="alert" role="alert">
                Couldn’t load the court and practice-area lists. Refresh the page to try again.
              </div>
            )}
            <FormField id="full_name" label="Full name (with honorific)" placeholder="e.g. Adv. Tanvir Ahmed" autoComplete="name"
              value={values.full_name} onChange={onChange} error={errors.full_name} />
            <FormField id="phone" label="Official mobile number" type="tel" placeholder="+880 1712-345678" autoComplete="tel"
              hint="Used for 2FA and case verification." value={values.phone} onChange={onChange} error={errors.phone} />
            <FormField id="email" label="Official email address" type="email" placeholder="lawyer@example.com" autoComplete="email"
              value={values.email} onChange={onChange} error={errors.email} />
            <FormField id="primary_court" label="Primary court / jurisdiction" as="select"
              value={values.primary_court} onChange={onChange} error={errors.primary_court}>
              <option value="">{ref.loading ? 'Loading courts…' : 'Select primary court'}</option>
              {ref.courts.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </FormField>
            <FormField id="preferred_language" label="Preferred language" as="select"
              value={values.preferred_language} onChange={onChange} error={errors.preferred_language}>
              <option value="en">English</option>
              <option value="bn">বাংলা</option>
            </FormField>
          </>
        )}

        {step === 2 && (
          <>
            <FormField id="bar_council_no" label="Bar Council Sanad / registration no." placeholder="e.g. BC-2018-9412"
              value={values.bar_council_no} onChange={onChange} error={errors.bar_council_no} />
            <FormField id="bar_association" label="Bar association membership" list="bar-associations" autoComplete="off"
              placeholder="Select or type your bar association"
              value={values.bar_association} onChange={onChange} error={errors.bar_association} />
            <datalist id="bar-associations">
              {BAR_ASSOCIATIONS.map((name) => <option key={name} value={name} />)}
            </datalist>

            <div className="k" id="areas-label">Primary legal practice areas</div>
            <div className="chp" role="group" aria-labelledby="areas-label" tabIndex={-1}
              data-invalid={errors.practice_areas ? 'true' : undefined}>
              {ref.areas.map((a) => (
                <button type="button" key={a.id} className={values.practice_areas.includes(a.id) ? 'on' : ''}
                  aria-pressed={values.practice_areas.includes(a.id)} onClick={() => toggleArea(a.id)}>
                  {a.name_en}
                </button>
              ))}
            </div>
            {errors.practice_areas && <div className="fe" role="alert">{errors.practice_areas}</div>}

            <FormField id="chamber_address" label="Chamber room / office address" placeholder="e.g. Chambers 405, Supreme Court Bar"
              autoComplete="street-address" value={values.chamber_address} onChange={onChange} error={errors.chamber_address} />
          </>
        )}

        {step === 3 && (
          <>
            <FormField id="password" label="Create master password" type="password" autoComplete="new-password"
              hint="At least 8 characters with upper and lower case letters, a number and a special character."
              value={values.password} onChange={onChange} error={errors.password} />
            <PasswordStrength password={values.password} />
            <FormField id="password_confirm" label="Confirm password" type="password" autoComplete="new-password"
              value={values.password_confirm} onChange={onChange} error={errors.password_confirm} />
            <FormField id="consultation_fee" label="Chamber consultation fee per session (BDT)" inputMode="decimal"
              placeholder="e.g. 5000" hint="Optional - you can change it later."
              value={values.consultation_fee} onChange={onChange} error={errors.consultation_fee} />

            <div className="ck" style={{ marginTop: 20 }}>
              <input id="two_factor_enabled" name="two_factor_enabled" type="checkbox"
                checked={values.two_factor_enabled} onChange={onChange} />
              <label htmlFor="two_factor_enabled">Enable 2-factor authentication via your registered SMS and WhatsApp number.</label>
            </div>
            <div className="ck">
              <input id="accept_terms" name="accept_terms" type="checkbox" checked={values.accept_terms} onChange={onChange}
                aria-invalid={errors.accept_terms ? 'true' : undefined}
                aria-describedby={errors.accept_terms ? 'accept_terms-error' : undefined} />
              <label htmlFor="accept_terms">
                I accept the Bangladesh Bar Council Canons of Professional Conduct and the LawAid Chamber Agreement.
              </label>
            </div>
            {errors.accept_terms && <div className="fe" id="accept_terms-error" role="alert">{errors.accept_terms}</div>}
          </>
        )}

        {general && <div className="alert" role="alert">{general}</div>}

        <div className="btr">
          {step > 1 && (
            <button type="button" className="bk2" onClick={() => { setErrors({}); setGeneral(''); setStep(step - 1) }}>
              ← Back
            </button>
          )}
          <button type="submit" className="btn" disabled={submitting}>
            {step === 1 && 'Continue to Bar verification'}
            {step === 2 && 'Continue to security'}
            {step === 3 && (submitting ? 'Creating account…' : 'Complete registration')}
          </button>
        </div>
      </form>

      {step === 1 && (
        <>
          <hr />
          <p className="foot">Already registered with LawAid? <Link to="/login">Log in</Link></p>
        </>
      )}
    </AuthShell>
  )
}
