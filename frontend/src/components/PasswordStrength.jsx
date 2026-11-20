import { passwordScore } from '../utils/validators'

const LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong']

export default function PasswordStrength({ password }) {
  if (!password) return null
  const score = passwordScore(password)
  return (
    <>
      <div className="fg" aria-live="polite">Strength: {LABELS[score]}</div>
      <div className="str" aria-hidden="true">
        {[0, 1, 2, 3].map((i) => <i key={i} className={i < score ? '' : 'n'} />)}
      </div>
    </>
  )
}
