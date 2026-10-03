import { useEffect, useState } from 'react'
import { api } from '../api'

export default function VenueBasics() {
  const [venue, setVenue] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .venueBasics()
      .then(setVenue)
      .catch((err) => setError(err.message || 'Could not load venue'))
  }, [])

  return (
    <div className="card">
      <h1>Venue basics</h1>
      <p className="muted">Admin view for the signed-in venue. Not a multi-tenant console.</p>
      {error && <div className="alert error">{error}</div>}
      {venue && (
        <dl className="basics">
          <div>
            <dt>Name</dt>
            <dd>{venue.name}</dd>
          </div>
          <div>
            <dt>City</dt>
            <dd>{venue.city || '—'}</dd>
          </div>
          <div>
            <dt>Timezone</dt>
            <dd>{venue.timezone}</dd>
          </div>
          <div>
            <dt>Default event</dt>
            <dd>
              {venue.default_event_name || '—'}
              {venue.default_event_date ? ` · ${venue.default_event_date}` : ''}
            </dd>
          </div>
          <div>
            <dt>Lost reports</dt>
            <dd>{venue.lost_report_count}</dd>
          </div>
          <div>
            <dt>Found items</dt>
            <dd>{venue.found_item_count}</dd>
          </div>
          <div>
            <dt>Suggested matches</dt>
            <dd>{venue.suggested_match_count}</dd>
          </div>
          <div>
            <dt>Staff accounts</dt>
            <dd>{venue.user_count}</dd>
          </div>
        </dl>
      )}
    </div>
  )
}
