import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Search() {
  const [q, setQ] = useState('')
  const [section, setSection] = useState('')
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function load(params = {}) {
    setLoading(true)
    setError('')
    try {
      const data = await api.listFound({
        venue_id: 1,
        ...(params.q ? { q: params.q } : {}),
        ...(params.section ? { section: params.section } : {}),
      })
      setItems(data)
    } catch (err) {
      setError(err.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load({})
  }, [])

  function onSearch(e) {
    e.preventDefault()
    load({ q, section })
  }

  return (
    <div>
      <div className="card">
        <h1>Search Found Items</h1>
        <p className="muted">
          Browse items logged by Demo Arena staff for tonight&apos;s Night Game.
        </p>
        <form onSubmit={onSearch} className="form-grid">
          <label className="full">
            Keyword
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="earbuds, wallet, keys…"
            />
          </label>
          <label>
            Section
            <input
              value={section}
              onChange={(e) => setSection(e.target.value)}
              placeholder="112"
            />
          </label>
          <div style={{ alignSelf: 'end' }}>
            <button type="submit" disabled={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Results ({items.length})</h2>
        {error && <div className="alert error">{error}</div>}
        {!error && items.length === 0 && (
          <p className="muted">No found items match yet.</p>
        )}
        <ul className="item-list">
          {items.map((item) => (
            <li key={item.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <strong>#{item.id}</strong>
                <span className="badge">{item.status}</span>
              </div>
              <div>{item.item_description}</div>
              <div className="seat-tag">
                Sec {item.section || '—'} · Row {item.row || '—'} · Seat{' '}
                {item.seat || '—'}
                {item.gate ? ` · ${item.gate}` : ''}
              </div>
              <div className="muted" style={{ fontSize: '0.85rem' }}>
                {item.event_name || 'Event'} · {item.event_date || '—'}
                {item.storage_location ? ` · Stored: ${item.storage_location}` : ''}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
