import { useState } from 'react'
import { api } from '../api'

const empty = {
  reporter_name: '',
  reporter_email: '',
  reporter_phone: '',
  item_description: '',
  category: '',
  color: '',
  brand: '',
  section: '',
  row: '',
  seat: '',
  gate: '',
  event_name: 'Night Game',
  event_date: '2026-10-01',
}

export default function ReportItem() {
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = {
        venue_id: 1,
        ...form,
        reporter_email: form.reporter_email || null,
        reporter_phone: form.reporter_phone || null,
        category: form.category || null,
        color: form.color || null,
        brand: form.brand || null,
        section: form.section || null,
        row: form.row || null,
        seat: form.seat || null,
        gate: form.gate || null,
        event_name: form.event_name || null,
        event_date: form.event_date || null,
      }
      const report = await api.createLost(payload)
      setSuccess(
        `Report #${report.id} submitted. We'll help Guest Services look near section ${
          report.section || '—'
        }.`,
      )
      setForm(empty)
    } catch (err) {
      setError(err.message || 'Could not submit report')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h1>Report a Lost Item</h1>
      <p className="muted">
        Tell us what you lost and where you were sitting during the Night Game.
        No account required.
      </p>
      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      <form onSubmit={onSubmit} className="form-grid">
        <label className="full">
          Your name *
          <input
            required
            value={form.reporter_name}
            onChange={(e) => set('reporter_name', e.target.value)}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.reporter_email}
            onChange={(e) => set('reporter_email', e.target.value)}
          />
        </label>
        <label>
          Phone
          <input
            value={form.reporter_phone}
            onChange={(e) => set('reporter_phone', e.target.value)}
          />
        </label>
        <label className="full">
          What did you lose? *
          <textarea
            required
            value={form.item_description}
            onChange={(e) => set('item_description', e.target.value)}
            placeholder="e.g. Black wallet with team lanyard"
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
          Brand
          <input value={form.brand} onChange={(e) => set('brand', e.target.value)} />
        </label>
        <label>
          Section *
          <input
            value={form.section}
            onChange={(e) => set('section', e.target.value)}
            placeholder="112"
          />
        </label>
        <label>
          Row
          <input
            value={form.row}
            onChange={(e) => set('row', e.target.value)}
            placeholder="G"
          />
        </label>
        <label>
          Seat
          <input
            value={form.seat}
            onChange={(e) => set('seat', e.target.value)}
            placeholder="14"
          />
        </label>
        <label>
          Gate / entrance
          <input
            value={form.gate}
            onChange={(e) => set('gate', e.target.value)}
            placeholder="Gate C"
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
            {loading ? 'Submitting…' : 'Submit lost report'}
          </button>
        </div>
      </form>
    </div>
  )
}
