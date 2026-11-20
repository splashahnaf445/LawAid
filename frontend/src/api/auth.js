/**
 * LawAid registration API.
 *
 * Integration note (integration/merge-all):
 *  - registerClient / registerLawyer / reference data: Usama (SYS-18). Ahnaf's functions with the
 *    same names were dropped because the registration pages that called them were replaced by
 *    Usama's pages (see the PR). registerLawyer sends multipart so the NID and Bar Council
 *    certificate (Ahnaf, SYS-21) are uploaded with the form.
 *  - Login / logout / current user: use Saker's useAuth() from src/auth/AuthContext.jsx (the one
 *    login flow). Ahnaf's localStorage-based login(), getCurrentUser() and logout() that lived
 *    here were replaced by it.
 */
import http from './http'

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
