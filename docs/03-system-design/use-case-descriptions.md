# Major Use Case Descriptions

## UC-1 · Book Appointment
**Primary actor:** Client · **Other stakeholders:** Lawyer (organized, conflict-free bookings), Admin (traceable bookings for disputes)

Lets a client schedule a consultation with a verified lawyer, choosing date, time and format (video, audio, chat or in-person) without phone calls or manual coordination.

| | |
|---|---|
| **Pre-conditions** | Client registered and logged in · verified lawyer selected · lawyer availability visible |
| **Success scenario** | 1. Client opens lawyer profile and views slots → 2. picks date, time and format → 3. system confirms and reserves the slot → 4. client pays to confirm → 5. lawyer receives the request and accepts → 6. system sends confirmation and reminders to both |
| **Alternatives** | Slot taken → client picks another · lawyer declines/reschedules → client notified with alternatives · payment fails → booking held temporarily, then released |
| **Post-conditions** | Appointment visible on both dashboards · both parties get reminders |

## UC-2 · Ask AI Legal Chatbot
**Primary actor:** General public / Client · **Other stakeholders:** Admin (answers stay within safe, general-information limits)

Free, bilingual (Bangla/English) assistant that explains basic laws, rights and consequences, with no paid consultation needed.

| | |
|---|---|
| **Pre-conditions** | Chatbot accessible without login · user has a legal question |
| **Success scenario** | 1. User opens chatbot and picks a language → 2. asks a question → 3. system queries the AI API and returns a plain-language explanation → 4. prompts the user to book a verified lawyer if the matter needs case-specific advice |
| **Alternatives** | Out-of-scope query (specific advice or representation) → disclaimer + redirect to lawyer search/booking · AI service down → error message and retry suggestion |
| **Post-conditions** | User receives general legal information · optionally routed to book a lawyer |

## UC-3 · Verify Lawyer Credentials
**Primary actor:** Admin · **Other stakeholders:** Lawyer (fair, timely review), Client (assurance that "verified" means credentialed)

| | |
|---|---|
| **Pre-conditions** | Lawyer completed registration and uploaded NID + Bar Council certificate · submission pending in admin panel |
| **Success scenario** | 1. Admin opens pending queue → 2. reviews NID and certificate → 3. confirms validity against Bar Council records → 4. system marks profile verified and shows the badge → 5. lawyer is notified and appears in client search |
| **Alternatives** | Invalid/incomplete documents → admin rejects, lawyer notified with reason · resubmission restarts the review |
| **Post-conditions** | Profile verified and public, or unverified pending resubmission · decision logged |
