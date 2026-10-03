import { useEffect, useState } from 'react'
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
  notes: '',
  event_name: 'Night Game',
  event_date: '2026-10-01',
}

function blankToNull(value) {
  return value ? value : null
}

export default function StaffFoundLog() {
  const [form, setForm] = useState(empty)
  const [photo, setPhoto] = useState(null)
  const [fileKey, setFileKey] = useState(0)
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function set(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function refresh() {
    const data = await api.listFound({ venue_id: 1 })
    setItems(data)
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message))
  }, [])

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = {
        venue_id: 1,
        item_description: form.item_description,
        category: blankToNull(form.category),
        color: blankToNull(form.color),
        brand: blankToNull(form.brand),
        section: blankToNull(form.section),
        row: blankToNull(form.row),
        seat: blankToNull(form.seat),
        gate: blankToNull(form.gate),
        storage_location: blankToNull(form.storage_location),
        notes: blankToNull(form.notes),
        event_name: blankToNull(form.event_name),
        event_date: blankToNull(form.event_date),
      }
      let item = await api.createFound(payload)
      if (photo) {
        item = await api.uploadFoundPhoto(item.id, photo)
      }
      setSuccess(
        `Logged found item #${item.id}` + (item.photo_path ? ' with photo' : '') + '.',
      )
      setForm(empty)
      setPhoto(null)
      setFileKey((key) => key + 1)
      await refresh()
    } catch (err) {
      setError(err.message || 'Could not log item')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h1>Staff Found Log</h1>
        <p className="muted">
          Log an item found in the stands, concourse, or at a gate during Night Game.
          Saving here recomputes suggested matches for the queue.
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
            Category *
            <select
              required
              value={form.category}
              onChange={(e) => set('category', e.target.value)}
            >
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
            Gate / entrance
            <input value={form.gate} onChange={(e) => set('gate', e.target.value)} />
          </label>
          <label>
            Event date *
            <input
              required
              type="date"
              value={form.event_date}
              onChange={(e) => set('event_date', e.target.value)}
            />
          </label>
          <label>
            Row
            <input value={form.row} onChange={(e) => set('row', e.target.value)} />
          </label>
          <label>
            Seat
            <input value={form.seat} onChange={(e) => set('seat', e.target.value)} />
          </label>
          <label className="full">
            Notes
            <textarea
              value={form.notes}
              onChange={(e) => set('notes', e.target.value)}
              placeholder="Where it was turned in, condition, anything written on it"
            />
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
            Photo
            <input
              key={fileKey}
              type="file"
              accept="image/*"
              onChange={(e) => setPhoto(e.target.files?.[0] || null)}
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
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <strong>#{item.id}</strong>
                <span className="badge">{item.status}</span>
              </div>
              <div>{item.item_description}</div>
              <div className="seat-tag">
                {item.category || 'No category'} · Sec {item.section || '—'} ·{' '}
                {item.gate || 'No gate'} · {item.event_date || '—'}
              </div>
              {item.notes && (
                <div className="muted" style={{ fontSize: '0.9rem' }}>
                  Notes: {item.notes}
                </div>
              )}
              {item.photo_path && (
                <img className="thumb" alt="" src={`/${item.photo_path}`} />
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
