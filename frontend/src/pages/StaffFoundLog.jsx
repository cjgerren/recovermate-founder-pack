import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const empty = {
  item_description: '',
  category: '',
  color: '',
  brand: '',
  section: '',
  row: '',
  seat: '',
  gate: '',
  storage_location: 'Guest Services — Main Concourse',
  event_name: 'Night Game',
  event_date: '2026-10-01',
}

export default function StaffFoundLog() {
  const token = localStorage.getItem('rm_token')
  const [form, setForm] = useState(empty)
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function refresh() {
    try {
      const data = await api.listFound({ venue_id: 1 })
      setItems(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = {
        venue_id: 1,
        ...form,
        category: form.category || null,
        color: form.color || null,
        brand: form.brand || null,
        section: form.section || null,
        row: form.row || null,
        seat: form.seat || null,
        gate: form.gate || null,
        storage_location: form.storage_location || null,
        event_name: form.event_name || null,
        event_date: form.event_date || null,
      }
      const item = await api.createFound(payload)
      setSuccess(`Logged found item #${item.id}`)
      setForm(empty)
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not log item')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {!token && (
        <div className="alert error">
          You can log items without signing in for this demo, but staff should{' '}
          <Link to="/login">log in</Link> so the entry is attributed.
        </div>
      )}

      <div className="card">
        <h1>Staff Found Log</h1>
        <p className="muted">
          Log an item found in the stands, concourse, or at a gate during Night
          Game.
        </p>
        {error && <div className="alert error">{error}</div>}
        {success && <div className="alert success">{success}</div>}

        <form onSubmit={onSubmit} className="form-grid">
          <label className="full">
            Item description *
            <textarea
              required
              value={form.item_description}
              onChange={(e) => set('item_description', e.target.value)}
              placeholder="Blue charging case found under seat"
            />
          </label>
          <label>
            Category
            <select value={form.category} onChange={(e) => set('category', e.target.value)}>
              <option value="">Select…</option>
              <option>Electronics</option>
              <option>Clothing</option>
              <option>Keys</option>
              <option>Wallet / ID</option>
              <option>Bag / Accessories</option>
              <option>Other</option>
            </select>
          </label>
          <label>
            Color
            <input value={form.color} onChange={(e) => set('color', e.target.value)} />
          </label>
          <label>
            Section
            <input value={form.section} onChange={(e) => set('section', e.target.value)} />
          </label>
          <label>
            Row
            <input value={form.row} onChange={(e) => set('row', e.target.value)} />
          </label>
          <label>
            Seat
            <input value={form.seat} onChange={(e) => set('seat', e.target.value)} />
          </label>
          <label>
            Gate / entrance
            <input value={form.gate} onChange={(e) => set('gate', e.target.value)} />
          </label>
          <label className="full">
            Storage location
            <input
              value={form.storage_location}
              onChange={(e) => set('storage_location', e.target.value)}
            />
          </label>
          <label>
            Event
            <input
              value={form.event_name}
              onChange={(e) => set('event_name', e.target.value)}
            />
          </label>
          <label>
            Event date
            <input
              type="date"
              value={form.event_date}
              onChange={(e) => set('event_date', e.target.value)}
            />
          </label>
          <div className="full">
            <button type="submit" disabled={loading}>
              {loading ? 'Saving…' : 'Log found item'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Recently logged ({items.length})</h2>
        <ul className="item-list">
          {items.map((item) => (
            <li key={item.id}>
              <strong>#{item.id}</strong> {item.item_description}
              <div className="seat-tag">
                Sec {item.section || '—'} · Row {item.row || '—'} · Seat{' '}
                {item.seat || '—'}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
