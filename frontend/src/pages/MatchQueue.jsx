import { useEffect, useState } from 'react'
import { api } from '../api'

export default function MatchQueue() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busyId, setBusyId] = useState(null)

  async function refresh() {
    const data = await api.listMatches('suggested')
    setRows(data)
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message || 'Could not load matches'))
  }, [])

  async function decide(id, action) {
    setError('')
    setMessage('')
    setBusyId(id)
    try {
      const updated = action === 'accept' ? await api.acceptMatch(id) : await api.rejectMatch(id)
      setMessage(
        action === 'accept'
          ? `Match #${updated.id} accepted. Lost #${updated.lost_report_id} is linked to found #${updated.found_item_id}.`
          : `Match #${updated.id} rejected.`,
      )
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not update match')
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div>
      <div className="card">
        <h1>Match queue</h1>
        <p className="muted">
          Suggested pairs for Demo Arena. A suggestion needs the same venue, the same
          category, an event date within one day, and a shared keyword in the
          description or location. Accept links the lost report to the found item.
          Reject leaves both records unlinked.
        </p>
        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message}</div>}
        {rows.length === 0 && !error && (
          <p className="muted">No suggested matches right now.</p>
        )}
      </div>

      {rows.map((row) => (
        <div className="card" key={row.id}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <h2 style={{ margin: 0 }}>Suggestion #{row.id}</h2>
            <span className="badge">{row.status}</span>
          </div>
          {row.notes && (
            <p className="muted" style={{ marginBottom: 0 }}>
              {row.notes}
            </p>
          )}
          <div className="match-grid">
            <div>
              <h3>Lost #{row.lost_report.id}</h3>
              <p>{row.lost_report.item_description}</p>
              <div className="seat-tag">
                {row.lost_report.category || 'No category'} · Sec{' '}
                {row.lost_report.section || '—'} · {row.lost_report.gate || 'No gate'}
              </div>
              <div className="muted">
                {row.lost_report.event_name || 'Event'} · {row.lost_report.event_date || '—'}
                <br />
                {row.lost_report.reporter_name}
                {row.lost_report.reporter_email ? ` · ${row.lost_report.reporter_email}` : ''}
              </div>
            </div>
            <div>
              <h3>Found #{row.found_item.id}</h3>
              <p>{row.found_item.item_description}</p>
              <div className="seat-tag">
                {row.found_item.category || 'No category'} · Sec{' '}
                {row.found_item.section || '—'} · {row.found_item.gate || 'No gate'}
              </div>
              <div className="muted">
                {row.found_item.event_name || 'Event'} · {row.found_item.event_date || '—'}
                {row.found_item.notes ? <><br />Notes: {row.found_item.notes}</> : null}
              </div>
            </div>
          </div>
          <div className="row-actions">
            <button
              type="button"
              disabled={busyId === row.id}
              onClick={() => decide(row.id, 'accept')}
            >
              Accept
            </button>
            <button
              type="button"
              className="danger"
              disabled={busyId === row.id}
              onClick={() => decide(row.id, 'reject')}
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
