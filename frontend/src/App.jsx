import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import ReportItem from './pages/ReportItem'
import Search from './pages/Search'
import StaffFoundLog from './pages/StaffFoundLog'

function App() {
  const navigate = useNavigate()
  const token = localStorage.getItem('rm_token')
  const name = localStorage.getItem('rm_name')

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
          <NavLink to="/staff/found">Staff Found Log</NavLink>
          {token ? (
            <>
              <span style={{ opacity: 0.85, fontSize: '0.9rem' }}>{name}</span>
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
          <Route path="/staff/found" element={<StaffFoundLog />} />
        </Routes>
      </main>

      <p className="footer-note">
        Week 1 Day 1 skeleton · No SMS / AI match / multi-tenant yet · Local demo only
      </p>
    </div>
  )
}

export default App
