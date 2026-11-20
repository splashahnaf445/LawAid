/**
 * LawAid authentication & registration API.
 *
 * Integration note (integration/merge-all):
 *  - registerClient / registerLawyer / reference data: Usama (SYS-18). Ahnaf's functions with the
 *    same names were dropped because the registration pages that called them were replaced by
 *    Usama's pages (see the PR). registerLawyer now sends multipart so the NID and Bar Council
 *    certificate (Ahnaf, SYS-21) are uploaded with the form.
 *  - login / getCurrentUser / logout: Ahnaf (SYS-21/22).
 */
import http, { apiFetch, authStorage } from './http'

export const registerClient = (payload) =>
  http.post('/auth/register/client/', payload).then((r) => r.data)

/** @param {FormData} formData - all form fields plus nid_document and bar_certificate_document */
export const registerLawyer = (formData) =>
  http
    .post('/auth/register/lawyer/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    .then((r) => r.data)

// Reference data for the lawyer form dropdowns
export const listCourts = () => http.get('/reference/courts/').then((r) => r.data)
export const listPracticeAreas = () => http.get('/reference/practice-areas/').then((r) => r.data)

// ---- Ahnaf (SYS-21/22) ----------------------------------------------------
export async function login(email, password) {
  const data = await apiFetch('/api/auth/token/', {
    method: 'POST',
    body: { email, password },
  })

  if (data.access) {
    authStorage.setToken(data.access)
  }
  if (data.user) {
    authStorage.setUser(data.user)
  }
  return data
}

export async function getCurrentUser() {
  const user = await apiFetch('/api/auth/me/')
  authStorage.setUser(user)
  return user
}

export function logout() {
  authStorage.clearAll()
  window.dispatchEvent(new CustomEvent('lawaid:auth_changed', { detail: null }))
}
