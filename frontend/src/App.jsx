import { NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import RequireAuth from './RequireAuth'
import Home from './pages/Home'
import Login from './pages/Login'
import ReportItem from './pages/ReportItem'
import Search from './pages/Search'
import StaffFoundLog from './pages/StaffFoundLog'
import MatchQueue from './pages/MatchQueue'
import VenueBasics from './pages/VenueBasics'

function App() {
  const navigate = useNavigate()
  // Re-read the session whenever the route changes (login/logout).
  useLocation()
  const token = localStorage.getItem('rm_token')
  const name = localStorage.getItem('rm_name')
  const role = localStorage.getItem('rm_role')

  function logout() {
    localStorage.removeItem('rm_token')
    localStorage.removeItem('rm_name')
    localStorage.removeItem('rm_role')
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="brand">RecoverMate</span>
          <span className="event-pill">Demo Arena · Night Game</span>
        </div>
        <nav>
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/report">Report Lost Item</NavLink>
          <NavLink to="/search">Search Found Items</NavLink>
          {token && (
            <>
              <NavLink to="/staff/found">Found Log</NavLink>
              <NavLink to="/staff/matches">Match Queue</NavLink>
            </>
          )}
          {token && role === 'admin' && (
            <NavLink to="/admin/venue">Venue</NavLink>
          )}
          {token ? (
            <>
              <span style={{ opacity: 0.85, fontSize: '0.9rem' }}>
                {name} ({role})
              </span>
              <button
                type="button"
                className="secondary"
                style={{ padding: '0.35rem 0.7rem' }}
                onClick={logout}
              >
                Log out
              </button>
            </>
          ) : (
            <NavLink to="/login">Staff Login</NavLink>
          )}
        </nav>
      </header>

      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/report" element={<ReportItem />} />
          <Route path="/search" element={<Search />} />
          <Route
            path="/staff/found"
            element={
              <RequireAuth>
                <StaffFoundLog />
              </RequireAuth>
            }
          />
          <Route
            path="/staff/matches"
            element={
              <RequireAuth>
                <MatchQueue />
              </RequireAuth>
            }
          />
          <Route
            path="/admin/venue"
            element={
              <RequireAuth admin>
                <VenueBasics />
              </RequireAuth>
            }
          />
        </Routes>
      </main>

      <p className="footer-note">
        Week 1 Days 3–7 · Rule-based match queue · No SMS, email claims, Stripe, or AI
      </p>
    </div>
  )
}

export default App
