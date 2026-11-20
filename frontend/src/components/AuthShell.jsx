import { Link } from 'react-router-dom'

// The centred dark card used by every auth screen in the prototype (login / register).
export default function AuthShell({ subtitle, children, backTo = '/', backLabel = '← Back to LawAid' }) {
  return (
    <div className="login">
      <div>
        <div className="lg"><i aria-hidden="true">⚖</i></div>
        <h1>LawAid</h1>
        <div className="sub">{subtitle}</div>
        <div className="lbox">{children}</div>
        <Link className="back" to={backTo}>{backLabel}</Link>
      </div>
    </div>
  )
}
