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

function blankToNull(value) {
  return value ? value : null
}

export default function ReportItem() {
  const [form, setForm] = useState(empty)
  const [photo, setPhoto] = useState(null)
  const [fileKey, setFileKey] = useState(0)
  const [error, setError] = useState('')
  const [confirmation, setConfirmation] = useState(null)
  const [loading, setLoading] = useState(false)

  function set(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setConfirmation(null)
    setLoading(true)
    try {
      const payload = {
        venue_id: 1,
        reporter_name: form.reporter_name,
        reporter_email: blankToNull(form.reporter_email),
        reporter_phone: blankToNull(form.reporter_phone),
        item_description: form.item_description,
        category: blankToNull(form.category),
        color: blankToNull(form.color),
        brand: blankToNull(form.brand),
        section: blankToNull(form.section),
        row: blankToNull(form.row),
        seat: blankToNull(form.seat),
        gate: blankToNull(form.gate),
        event_name: blankToNull(form.event_name),
        event_date: blankToNull(form.event_date),
      }
      let report = await api.createLost(payload)
      let photoNote = 'No photo attached'
      if (photo) {
        report = await api.uploadLostPhoto(report.id, photo)
        photoNote = 'Photo saved'
      }
      setConfirmation({ ...report, photoNote })
      setForm(empty)
      setPhoto(null)
      setFileKey((key) => key + 1)
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
        No account required. Category helps staff suggestions, but you can leave it blank.
      </p>
      {error && <div className="alert error">{error}</div>}
      {confirmation && (
        <div className="alert success">
          <p className="report-id">
            Report ID <strong>#{confirmation.id}</strong>
          </p>
          <div>
            {confirmation.item_description}
            <br />
            Contact: {confirmation.reporter_email || 'no email'} ·{' '}
            {confirmation.reporter_phone || 'no phone'}
            <br />
            Sec {confirmation.section || '—'} · Row {confirmation.row || '—'} · Seat{' '}
            {confirmation.seat || '—'} · {confirmation.gate || 'no gate'}
            <br />
            {confirmation.event_name || 'Event'} · {confirmation.event_date || '—'}
            {confirmation.category ? ` · ${confirmation.category}` : ''}
            <br />
            {confirmation.photoNote}
          </div>
          {confirmation.photo_path && (
            <img
              className="thumb"
              alt="Uploaded lost item"
              src={`/${confirmation.photo_path}`}
            />
          )}
        </div>
      )}

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
          Section
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
        <label className="full">
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
            {loading ? 'Submitting…' : 'Submit lost report'}
          </button>
        </div>
      </form>
    </div>
  )
}
