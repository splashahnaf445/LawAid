/**
 * Turn an axios error into { fields, general }.
 *  - fields:  { fieldName: 'message' } for DRF 400 responses ({ email: ["..."] })
 *  - general: a message for everything that is not tied to a visible field
 * Fields not in `knownFields` are folded into `general` so no error is ever swallowed.
 */
export function parseApiError(err, knownFields = []) {
  const res = err?.response
  if (!res) return { fields: {}, general: 'Cannot reach the server. Check your connection and try again.' }
  if (res.status === 429) {
    return { fields: {}, general: 'Too many attempts. Please wait a while and try again.' }
  }
  if (res.status === 400 && res.data && typeof res.data === 'object') {
    const fields = {}
    const general = []
    for (const [key, value] of Object.entries(res.data)) {
      const message = Array.isArray(value) ? value.join(' ') : String(value)
      if (knownFields.includes(key)) fields[key] = message
      else general.push(message)
    }
    return { fields, general: general.join(' ') }
  }
  return { fields: {}, general: 'Something went wrong on our side. Please try again.' }
}
