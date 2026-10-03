import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@demoarena.example')
  const [password, setPassword] = useState('DemoArena2026!')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.login(email, password)
      localStorage.setItem('rm_token', data.access_token)
      localStorage.setItem('rm_name', data.full_name)
      localStorage.setItem('rm_role', data.role)
      navigate('/staff/matches')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ maxWidth: 420, margin: '0 auto' }}>
      <h1>Staff Login</h1>
      <p className="muted">Demo Arena guest services &amp; gate staff</p>
      {error && <div className="alert error">{error}</div>}
      <form onSubmit={onSubmit} className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="username"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="muted" style={{ marginTop: '1rem', marginBottom: 0, fontSize: '0.85rem' }}>
        Admin: admin@demoarena.example / DemoArena2026!
        <br />
        Staff: staff@demoarena.example / StaffNight2026!
      </p>
    </div>
  )
}
