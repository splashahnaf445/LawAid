/**
 * LawAid HTTP layer.
 *
 * Integration note (integration/merge-all): ONE login flow - Saker's cookie-based session
 * (src/auth/AuthContext.jsx + src/api/client.js). The access token lives in memory
 * (src/auth/tokenStore.js) and is renewed from the httpOnly refresh cookie.
 *  - default export `http`: Usama's axios instance (registration + reference data).
 *  - `authStorage` / `apiFetch`: Ahnaf's helpers (lawyer directory, admin verification),
 *    now reading Saker's in-memory token instead of localStorage, and refreshing the
 *    session once on a 401 like Saker's axios client.
 * Base URL: the backend has no /v1 prefix, so the default is `/api` (Vite proxies it).
 */
import axios from 'axios'
import { getAccessToken, setAccessToken } from '../auth/tokenStore'
import { authEvents, refreshSession } from './client'

// Ahnaf's token helper, backed by Saker's in-memory token store.
export const authStorage = {
  getToken: () => getAccessToken(),
  setToken: (token) => setAccessToken(token),
  clearToken: () => setAccessToken(null),
  clearAll: () => setAccessToken(null),
}

// ---- Usama (SYS-18): axios instance ---------------------------------------
const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Token header - harmless for public endpoints.
http.interceptors.request.use((config) => {
  const token = authStorage.getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default http

// ---- Ahnaf (SYS-21/22): fetch wrapper --------------------------------------
async function send(url, options) {
  const headers = { ...options.headers }

  const token = authStorage.getToken()
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Handle FormData vs JSON
  let body = options.body
  if (body && !(body instanceof FormData) && typeof body === 'object') {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }

  return fetch(url, { ...options, headers, body })
}

export async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') || endpoint.startsWith('/') ? endpoint : `/api/${endpoint}`

  let response = await send(url, options)
  if (response.status === 401) {
    // Integration: renew the access token from Saker's refresh cookie once, then retry.
    try {
      await refreshSession()
      response = await send(url, options)
    } catch {
      authEvents.dispatchEvent(new Event('expired'))
    }
  }

  // Parse response
  let data
  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    data = await response.json()
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    const error = new Error((data && data.detail) || response.statusText || 'Request failed')
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}
