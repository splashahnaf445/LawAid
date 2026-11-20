import http from './http'

export const registerClient = (payload) =>
  http.post('/auth/register/client/', payload).then((r) => r.data)

export const registerLawyer = (payload) =>
  http.post('/auth/register/lawyer/', payload).then((r) => r.data)

// Reference data for the lawyer form dropdowns
export const listCourts = () => http.get('/reference/courts/').then((r) => r.data)
export const listPracticeAreas = () => http.get('/reference/practice-areas/').then((r) => r.data)
