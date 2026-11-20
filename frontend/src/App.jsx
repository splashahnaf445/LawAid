import { Navigate, Route, Routes } from 'react-router-dom'
import AuthShell from './components/AuthShell.jsx'
import Landing from './pages/Landing.jsx'
import RegisterClient from './pages/RegisterClient.jsx'
import RegisterLawyer from './pages/RegisterLawyer.jsx'
import RoleSelect from './pages/RoleSelect.jsx'

// Placeholder until the login ticket (FR-4) lands.
function LoginPlaceholder() {
  return (
    <AuthShell subtitle="LOG IN">
      <h2>Log in</h2>
      <small>Login arrives with the next ticket. Your account is ready for it.</small>
    </AuthShell>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/register" element={<RoleSelect />} />
      <Route path="/register/client" element={<RegisterClient />} />
      <Route path="/register/lawyer" element={<RegisterLawyer />} />
      <Route path="/login" element={<LoginPlaceholder />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
