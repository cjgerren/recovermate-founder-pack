const API_BASE = import.meta.env.VITE_API_BASE || ''

function authHeaders() {
  const token = localStorage.getItem('rm_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
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
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || JSON.stringify(body)
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  if (res.status === 204) return null
  return res.json()
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
  listLost: (venueId = 1) => request(`/api/lost-reports?venue_id=${venueId}`),
  createLost: (payload) =>
    request('/api/lost-reports', { method: 'POST', body: JSON.stringify(payload) }),
  listFound: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/api/found-items${q ? `?${q}` : ''}`)
  },
  createFound: (payload) =>
    request('/api/found-items', { method: 'POST', body: JSON.stringify(payload) }),
}
