const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export function getToken(): string | null {
  return localStorage.getItem('token')
}

export function setToken(token: string | null) {
  if (!token) localStorage.removeItem('token')
  else localStorage.setItem('token', token)
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', headers.get('Content-Type') ?? 'application/json')

  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const url = API_BASE_URL ? `${API_BASE_URL}${path}` : path
  const resp = await fetch(url, { ...init, headers })
  const contentType = resp.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await resp.json().catch(() => null) : await resp.text().catch(() => null)

  if (!resp.ok) {
    const message = typeof body === 'string' ? body : (body?.detail ?? 'Request failed')
    throw new Error(message)
  }
  return body
}
