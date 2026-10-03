import { Navigate } from 'react-router-dom'

export default function RequireAuth({ children, admin = false }) {
  const token = localStorage.getItem('rm_token')
  const role = localStorage.getItem('rm_role')
  if (!token) return <Navigate to="/login" replace />
  if (admin && role !== 'admin') {
    return (
      <div className="card">
        <h1>Venue basics</h1>
        <div className="alert error">
          Admin role required. Staff can log found items and work the match queue.
        </div>
      </div>
    )
  }
  return children
}
