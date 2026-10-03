import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function Home() {
  const [venue, setVenue] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api
      .venues()
      .then((list) => setVenue(list[0] || null))
      .catch(() => setVenue(null))
    api
      .health()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }))
  }, [])

  return (
    <div>
      <div className="card">
        <h1>Lost something at the arena?</h1>
        <p className="muted">
          RecoverMate helps guests and venue staff reconnect with items left behind
          during tonight&apos;s event.
        </p>
        {venue && (
          <p>
            <strong>{venue.name}</strong>
            {venue.city ? ` · ${venue.city}` : ''}
            {venue.default_event_name ? (
              <>
                {' '}
                · <span className="badge">{venue.default_event_name}</span>
                {venue.default_event_date ? ` · ${venue.default_event_date}` : ''}
              </>
            ) : null}
          </p>
        )}
        <div className="hero-actions">
          <Link className="btn" to="/report">
            Report a Lost Item
          </Link>
          <Link className="btn" to="/search" style={{ background: '#5a7fa8' }}>
            Search Found Items
          </Link>
          <Link className="btn secondary" to="/staff/found">
            Staff: Log Found Item
          </Link>
          <Link className="btn secondary" to="/staff/matches">
            Staff: Match Queue
          </Link>
        </div>
      </div>

      <div className="card">
        <h2>How it works</h2>
        <ol className="muted">
          <li>Guest reports a lost item with section, row, seat, and an optional photo. No login.</li>
          <li>Staff logs found items (category, location, date, notes, photo).</li>
          <li>RecoverMate suggests matches. Staff accept or reject them in the queue.</li>
        </ol>
        <p className="muted" style={{ marginBottom: 0 }}>
          API status:{' '}
          <strong>{health?.status || '…'}</strong>
          {health?.venue_seeded != null &&
            ` · Demo Arena seeded: ${health.venue_seeded ? 'yes' : 'no'}`}
        </p>
      </div>
    </div>
  )
}
