const API_BASE = import.meta.env.VITE_API_BASE || ''

function authHeaders() {
  const token = localStorage.getItem('rm_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseBody(res) {
  if (res.status === 204) return null
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

function errorDetail(body, fallback) {
  if (!body) return fallback
  if (typeof body === 'string') return body
  const detail = body.detail
  if (!detail) return JSON.stringify(body)
  if (typeof detail === 'string') return detail
  return JSON.stringify(detail)
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })
  const body = await parseBody(res)
  if (!res.ok) {
    throw new Error(errorDetail(body, res.statusText))
  }
  return body
}

async function upload(path, file) {
  const data = new FormData()
  data.append('file', file)
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: authHeaders(),
    body: data,
  })
  const body = await parseBody(res)
  if (!res.ok) {
    throw new Error(errorDetail(body, res.statusText))
  }
  return body
}

export const api = {
  health: () => request('/health'),
  login: (email, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => request('/api/auth/me'),
  venues: () => request('/api/venues'),
  venueBasics: () => request('/api/admin/venue'),
  listLost: (venueId = 1) => request(`/api/lost-reports?venue_id=${venueId}`),
  createLost: (payload) =>
    request('/api/lost-reports', { method: 'POST', body: JSON.stringify(payload) }),
  uploadLostPhoto: (id, file) => upload(`/api/lost-reports/${id}/photo`, file),
  listFound: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, value]) => value !== '' && value != null),
      ),
    ).toString()
    return request(`/api/found-items${q ? `?${q}` : ''}`)
  },
  createFound: (payload) =>
    request('/api/found-items', { method: 'POST', body: JSON.stringify(payload) }),
  uploadFoundPhoto: (id, file) => upload(`/api/found-items/${id}/photo`, file),
  listMatches: (status = 'suggested') =>
    request(`/api/matches${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  acceptMatch: (id) => request(`/api/matches/${id}/accept`, { method: 'POST' }),
  rejectMatch: (id) => request(`/api/matches/${id}/reject`, { method: 'POST' }),
}
