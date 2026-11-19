# LawAid API contract (SYS-16)

This folder is the REST contract between the LawAid frontend (React) and backend (Django REST Framework). The aim is that frontend and backend can be built in parallel against the same spec.

| File | What it is |
|---|---|
| [`openapi.yaml`](openapi.yaml) | The contract, OpenAPI 3.0.3. It covers 92 operations: 14 implemented and 78 planned. |
| [`redocly.yaml`](redocly.yaml) | Lint settings for the spec (see [Validate](#validate)). |
| `README.md` | This guide: conventions, endpoint list, known differences and decisions. |

**Where names come from:** `db/schema.sql` and `db/seed.sql` on `main`. All example data is fake and follows the seed's style.

## How to view it

- **Swagger Editor (no install).** Open <https://editor.swagger.io>, then *File → Import file* and pick `docs/api/openapi.yaml`.
- **VS Code.** Install the *OpenAPI (Swagger) Editor* extension (42Crunch), open `openapi.yaml`, and click the preview icon at the top right. The *Redocly OpenAPI* extension also works.
- **Static HTML page.** From the repo root:
  ```bash
  npx @redocly/cli build-docs docs/api/openapi.yaml --config docs/api/redocly.yaml -o api-docs.html
  ```
  This writes `api-docs.html` in the current folder. Open it in a browser, and don't commit it.

### Validate

```bash
npx @redocly/cli lint docs/api/openapi.yaml --config docs/api/redocly.yaml
```

This gives 0 errors and 0 warnings. Without `--config`, Redocly reports 77 `no-path-trailing-slash` "errors". That style rule conflicts with Django, whose URLs really end in `/`; see the decisions below.

## How to read an operation

Every operation carries these extension fields:

| Field | Meaning |
|---|---|
| `x-status` | `implemented` means the code exists and the entry describes exactly what it does today. `planned` means it is not written yet and the entry is a proposal. |
| `x-branch`, `x-merged-to-main` | Only on implemented operations: which branch holds the code, and whether it is on `main` yet. |
| `x-owner` | Who builds or owns it. `unassigned` means the Jira ticket has no assignee yet. |
| `x-jira` | The SYS ticket. |
| `x-roles` | Who may call it: `public`, `client`, `lawyer`, `admin`. |

## Conventions

| Topic | Rule |
|---|---|
| **Base URL** | `http://localhost:8000` in development. All paths start with `/api/`, except `GET /`. The React app uses `VITE_API_URL`, default `http://localhost:8000/api`. |
| **Trailing slash** | Every path ends with `/` (Django `APPEND_SLASH`). A `POST` without the slash fails. |
| **Auth** | `POST /api/auth/token/` with `{email, password}` returns `{access, refresh}`. Send `Authorization: Bearer <access>`, with a space after `Bearer`. |
| **Token lifetimes** | Access tokens last 60 minutes and refresh tokens 7 days. Refreshing returns a **new refresh token**, because rotation is on. |
| **Token claims** | `user_id`, `token_type`, `exp`, `iat`, `jti`. There is no `role` claim, so call `GET /api/auth/me/` (planned) to get the role. |
| **Roles** | `client`, `lawyer`, `admin`. The server checks the role on every protected route, so frontend route guards only affect what is shown. |
| **Errors** | DRF defaults, shown in the table below. |
| **Pagination** | The **implemented** lists (`/api/lawyers/` and `/api/verification/pending-lawyers/`) are **not paginated**. They return `{count, results}` or `{count, filter, applications}`. **Planned** lists use DRF `PageNumberPagination`: `?page=N`, 10 per page, returning `{count, next, previous, results}`. Small bounded lists (courts, slots, hearings, etc.) return a plain array. |
| **Dates** | ISO 8601 with offset. Server time zone is `Asia/Dhaka`, so values look like `2026-11-20T15:05:00+06:00`. The badge's `verified_at` is UTC (`+00:00`). Plain dates use `YYYY-MM-DD`. |
| **IDs** | UUID strings. A lawyer's id is their user id (`lawyer_profiles.user_id = users.id`). Courts and practice areas use integer ids. |
| **Money** | BDT decimal **strings**, e.g. `"1500.00"` (DRF default). `avg_rating` is also a decimal string, e.g. `"4.70"`. |
| **Enums** | Lowercase values exactly as in `db/schema.sql`, e.g. `verification_status`: `pending` / `approved` / `rejected`. |
| **Phone numbers** | `+8801XXXXXXXXX`. The backend also accepts `01XXXXXXXXX` and normalises it. |
| **File uploads** | `multipart/form-data`. Verification documents must be PDF, PNG, JPG or JPEG, at most 15 MB, sent in the fields `nid_document` and `bar_certificate_document`. |
| **Private files** | NID and certificate files are encrypted at rest. Only admins can read them, through authenticated endpoints that stream the file (NFR-4). The SPA must fetch them with the `Authorization` header and open them as a blob, because a plain link won't send the header. |

**Error bodies**

| Status | Body | When |
|---|---|---|
| 400 | `{"field_name": ["message", ...], "non_field_errors": [...]}` | Validation failed |
| 401 | `{"detail": "Authentication credentials were not provided."}` or `{"detail": "...", "code": "token_not_valid"}` | No token, or the token is invalid or expired. This also happens on public endpoints if a bad token is sent. |
| 403 | `{"detail": "..."}`. A few implemented views use `{"error": "..."}`. | Logged in, but the role or ownership doesn't allow it |
| 404 | `{"detail": "Not found."}`. Some implemented views use `{"error": "..."}`. | Unknown id, or a lawyer that isn't verified, viewed by the public. Non-UUID ids get Django's HTML 404 page. |
| 409 | `{"detail": "..."}` | Planned endpoints only: the action isn't allowed in the current status |

## Endpoints

"Implemented (branch, not merged)" means the code exists on `lawyer_docupload_verify_badge` but is not on `main` yet.

**System**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/` | API root and module index | public | Ahnaf Shahriar | SYS-21 | implemented (branch, not merged) |

**Auth**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| POST | `/api/auth/register/client/` | Register a client account | public | Usama Abdullah | SYS-18 | planned |
| POST | `/api/auth/register/lawyer/` | Register a lawyer with NID and Bar Council certificate | public | Ahnaf Shahriar | SYS-21 | implemented (branch, not merged) |
| POST | `/api/auth/token/` | Log in (obtain JWT access and refresh tokens) | public | Ahnaf Shahriar | SYS-19 | implemented (branch, not merged) |
| POST | `/api/auth/token/refresh/` | Refresh the access token | public | Ahnaf Shahriar | SYS-19 | implemented (branch, not merged) |
| POST | `/api/auth/logout/` | Log out (revoke the refresh token) | client, lawyer, admin | Saker Munshi | SYS-19 | planned |
| GET | `/api/auth/me/` | Current user | client, lawyer, admin | Saker Munshi | SYS-19 | planned |
| POST | `/api/auth/password/forgot/` | Request a password reset link or code | public | Mashruba Aktar | SYS-20 | planned |
| POST | `/api/auth/password/reset/` | Set a new password with a reset token | public | Mashruba Aktar | SYS-20 | planned |
| POST | `/api/auth/me/deletion-request/` | Request deletion of my data | client, lawyer | unassigned | SYS-55 | planned |

**Lawyer Verification**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| POST | `/api/lawyers/me/verification-documents/` | Re-upload NID and Bar Council certificate after rejection | lawyer | Ahnaf Shahriar | SYS-21 | planned |
| GET | `/api/verification/stats/` | Verification overview counters | admin | Ahnaf Shahriar | SYS-57 | implemented (branch, not merged) |
| GET | `/api/verification/pending-lawyers/` | Admin verification queue | admin | Ahnaf Shahriar | SYS-57 | implemented (branch, not merged) |
| GET | `/api/verification/lawyers/{lawyer_id}/` | One lawyer's application (admin) | admin | Ahnaf Shahriar | SYS-57 | implemented (branch, not merged) |
| POST | `/api/verification/lawyers/{lawyer_id}/approve/` | Approve a lawyer | admin | Ahnaf Shahriar | SYS-57 | implemented (branch, not merged) |
| POST | `/api/verification/lawyers/{lawyer_id}/reject/` | Reject a lawyer with a reason | admin | Ahnaf Shahriar | SYS-57 | implemented (branch, not merged) |
| GET | `/api/verification/documents/{document_id}/view/` | View a verification document inline (admin) | admin | Ahnaf Shahriar | SYS-21 | implemented (branch, not merged) |
| GET | `/api/verification/documents/{document_id}/download/` | Download a verification document (admin) | admin | Ahnaf Shahriar | SYS-21 | implemented (branch, not merged) |

**Lawyers**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/lawyers/` | Public verified-lawyer directory | public | Ahnaf Shahriar | SYS-22 | implemented (branch, not merged) |
| GET | `/api/lawyers/me/` | My lawyer profile and verification status | lawyer | Ahnaf Shahriar | SYS-22 | implemented (branch, not merged) |
| PATCH | `/api/lawyers/me/` | Update my lawyer profile | lawyer | unassigned | SYS-23 | planned |
| GET | `/api/lawyers/{lawyer_id}/` | Lawyer profile with Verified badge | public | Ahnaf Shahriar | SYS-22 | implemented (branch, not merged) |
| GET | `/api/lawyers/me/dashboard/` | Lawyer dashboard counters | lawyer | unassigned | SYS-64 | planned |

**Reference Data**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/courts/` | List courts | public | unassigned | SYS-24 | planned |
| GET | `/api/practice-areas/` | List practice areas | public | unassigned | SYS-24 | planned |

**Availability**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/lawyers/{lawyer_id}/slots/` | Open slots of a verified lawyer | public | unassigned | SYS-27 | planned |
| GET | `/api/lawyers/me/slots/` | My availability slots | lawyer | unassigned | SYS-27 | planned |
| POST | `/api/lawyers/me/slots/` | Publish an availability slot | lawyer | unassigned | SYS-27 | planned |
| DELETE | `/api/lawyers/me/slots/{slot_id}/` | Remove an unbooked slot | lawyer | unassigned | SYS-27 | planned |

**Appointments**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/appointments/` | List my appointments | client, lawyer, admin | unassigned | SYS-28 | planned |
| POST | `/api/appointments/` | Book a consultation (reserve a slot) | client | unassigned | SYS-28 | planned |
| GET | `/api/appointments/{appointment_id}/` | Get an appointment | client, lawyer, admin | unassigned | SYS-28 | planned |
| POST | `/api/appointments/{appointment_id}/accept/` | Lawyer accepts a booking | lawyer | unassigned | SYS-29 | planned |
| POST | `/api/appointments/{appointment_id}/decline/` | Lawyer declines a booking | lawyer | unassigned | SYS-29 | planned |
| POST | `/api/appointments/{appointment_id}/reschedule/` | Lawyer proposes another slot | lawyer | unassigned | SYS-29 | planned |
| POST | `/api/appointments/{appointment_id}/reschedule/accept/` | Client accepts the proposed slot | client | unassigned | SYS-29 | planned |
| POST | `/api/appointments/{appointment_id}/cancel/` | Cancel a booking | client, lawyer | unassigned | SYS-30 | planned |
| POST | `/api/appointments/{appointment_id}/start/` | Start the consultation | lawyer | unassigned | SYS-31 | planned |
| POST | `/api/appointments/{appointment_id}/complete/` | Finish the consultation | lawyer | unassigned | SYS-30 | planned |
| POST | `/api/appointments/{appointment_id}/confirm-completion/` | Client confirms the session (releases escrow) | client | unassigned | SYS-40 | planned |
| GET | `/api/appointments/{appointment_id}/session/` | Get the consultation room | client, lawyer | unassigned | SYS-31 | planned |
| GET | `/api/appointments/{appointment_id}/history/` | Status history of an appointment | client, lawyer, admin | unassigned | SYS-30 | planned |

**SOS**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| POST | `/api/sos-requests/` | Raise an SOS request | client | unassigned | SYS-33 | planned |
| GET | `/api/sos-requests/{sos_id}/` | Get an SOS request | client, lawyer, admin | unassigned | SYS-33 | planned |
| POST | `/api/sos-requests/{sos_id}/accept/` | Lawyer accepts an SOS request | lawyer | unassigned | SYS-33 | planned |

**Chat**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/conversations/` | My conversations | client, lawyer | unassigned | SYS-32 | planned |
| POST | `/api/conversations/` | Start (or reopen) a conversation | client, lawyer | unassigned | SYS-32 | planned |
| GET | `/api/conversations/{conversation_id}/messages/` | Messages in a conversation | client, lawyer | unassigned | SYS-32 | planned |
| POST | `/api/conversations/{conversation_id}/messages/` | Send a message | client, lawyer | unassigned | SYS-32 | planned |
| POST | `/api/conversations/{conversation_id}/read/` | Mark a conversation as read | client, lawyer | unassigned | SYS-32 | planned |

**Cases**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/cases/` | List my cases | client, lawyer | unassigned | SYS-34 | planned |
| POST | `/api/cases/` | Open a case | lawyer | unassigned | SYS-34 | planned |
| GET | `/api/cases/{case_id}/` | Get a case | client, lawyer, admin | unassigned | SYS-34 | planned |
| PATCH | `/api/cases/{case_id}/` | Update a case (status, details) | lawyer | unassigned | SYS-37 | planned |
| GET | `/api/cases/{case_id}/hearings/` | Hearings of a case | client, lawyer | unassigned | SYS-35 | planned |
| POST | `/api/cases/{case_id}/hearings/` | Add a hearing date | lawyer | unassigned | SYS-35 | planned |
| PATCH | `/api/cases/{case_id}/hearings/{hearing_id}/` | Update a hearing (outcome, adjournment) | lawyer | unassigned | SYS-35 | planned |
| GET | `/api/cases/{case_id}/updates/` | Case timeline | client, lawyer | unassigned | SYS-37 | planned |
| POST | `/api/cases/{case_id}/updates/` | Post a timeline update | lawyer | unassigned | SYS-37 | planned |
| GET | `/api/cases/{case_id}/documents/` | Documents of a case | client, lawyer | unassigned | SYS-36 | planned |
| POST | `/api/cases/{case_id}/documents/` | Upload a case document | client, lawyer | unassigned | SYS-36 | planned |
| GET | `/api/cases/{case_id}/documents/{case_document_id}/download/` | Download a case document | client, lawyer | unassigned | SYS-36 | planned |

**Payments**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/payments/` | Payment history | client, lawyer, admin | unassigned | SYS-42 | planned |
| POST | `/api/payments/` | Start a sandbox payment for a booking | client | unassigned | SYS-38 | planned |
| POST | `/api/payment-gateways/{method}/callback/` | Payment gateway callback (IPN) | public | unassigned | SYS-39 | planned |
| GET | `/api/payments/{payment_id}/` | Get a payment | client, lawyer, admin | unassigned | SYS-42 | planned |
| GET | `/api/payments/{payment_id}/receipt/` | Get the receipt (JSON or PDF) | client, lawyer, admin | unassigned | SYS-41 | planned |
| GET | `/api/receipts/verify/{qr_token}/` | Verify a receipt from its QR code | public | unassigned | SYS-41 | planned |
| POST | `/api/payments/{payment_id}/disputes/` | Raise a payment dispute | client | unassigned | SYS-43 | planned |

**Notifications**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/notifications/` | My notifications | client, lawyer, admin | unassigned | SYS-53 | planned |
| POST | `/api/notifications/{notification_id}/read/` | Mark one notification as read | client, lawyer, admin | unassigned | SYS-53 | planned |
| POST | `/api/notifications/read-all/` | Mark all my notifications as read | client, lawyer, admin | unassigned | SYS-53 | planned |

**Reviews and Reports**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/lawyers/{lawyer_id}/reviews/` | Reviews of a lawyer | public | unassigned | SYS-49 | planned |
| POST | `/api/reviews/` | Rate a completed consultation | client | unassigned | SYS-49 | planned |
| POST | `/api/reports/` | Submit a confidential misconduct report | client | unassigned | SYS-50 | planned |

**Admin**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/admin/overview/` | Admin dashboard counters | admin | unassigned | SYS-60 | planned |
| GET | `/api/admin/users/` | List user accounts | admin | unassigned | SYS-58 | planned |
| DELETE | `/api/admin/users/{user_id}/` | Remove an account (soft delete) | admin | unassigned | SYS-58 | planned |
| POST | `/api/admin/users/{user_id}/suspend/` | Suspend an account | admin | unassigned | SYS-58 | planned |
| POST | `/api/admin/users/{user_id}/reactivate/` | Reactivate a suspended account | admin | unassigned | SYS-58 | planned |
| GET | `/api/admin/reports/` | Confidential reports queue | admin | unassigned | SYS-59 | planned |
| GET | `/api/admin/reports/{report_id}/` | Get a confidential report | admin | unassigned | SYS-59 | planned |
| PATCH | `/api/admin/reports/{report_id}/` | Record action on a report | admin | unassigned | SYS-59 | planned |
| GET | `/api/admin/disputes/` | Payment disputes queue | admin | unassigned | SYS-59 | planned |
| PATCH | `/api/admin/disputes/{dispute_id}/` | Resolve a payment dispute | admin | unassigned | SYS-59 | planned |
| GET | `/api/admin/audit-logs/` | Audit log | admin | unassigned | SYS-54 | planned |
| GET | `/api/admin/ai-messages/` | Chatbot answers flagged for review | admin | unassigned | SYS-48 | planned |

**AI Assistant**

| Method | Path | What it does | Roles | Owner | Jira | Status |
|---|---|---|---|---|---|---|
| GET | `/api/ai/conversations/` | My chatbot conversations | client, lawyer | unassigned | SYS-44 | planned |
| POST | `/api/ai/conversations/` | Start a chatbot conversation | public, client, lawyer | unassigned | SYS-47 | planned |
| GET | `/api/ai/conversations/{ai_conversation_id}/messages/` | Messages of a chatbot conversation | public, client, lawyer | unassigned | SYS-44 | planned |
| POST | `/api/ai/conversations/{ai_conversation_id}/messages/` | Ask the chatbot | public, client, lawyer | unassigned | SYS-44 | planned |
| POST | `/api/ai/recommendations/` | AI lawyer recommendation | client | unassigned | SYS-26 | planned |

## Frontend differences

These come from the React client on `feature/LAW-12-modular-architecture` (`frontend/src/api/client.js`, `authentication/AuthContect.jsx`). Where a backend implementation exists, the contract follows the backend. The client needs these changes to work with it:

| Area | Current frontend | Contract | Change needed |
|---|---|---|---|
| Login | `POST /auth/login/` with `{email, password, remember, portal}`, expects `{access, user}` | `POST /api/auth/token/` with `{email, password}`, returns `{access, refresh}` | Call the token endpoint, then `GET /api/auth/me/` for the user and role. `remember` and `portal` are ignored. |
| Refresh | `POST /auth/refresh/` with no body (cookie), expects `{access, user}` | `POST /api/auth/token/refresh/` with `{refresh}`, returns `{access, refresh}` | Keep the refresh token client-side and send it in the body. Store the rotated one. |
| Logout | `POST /auth/logout/` with no body | `POST /api/auth/logout/` with `{refresh}` (planned) | Send the refresh token. |
| Auth header | `` `Bearer${token}` `` | `Bearer <token>` | Add the missing space. Every protected call fails today without it. |
| Refresh handler | `setAccessToken(res.data,access)` | the `access` field | Typo: should be `res.data.access`. |
| Imports and events | `client.js` imports `../auth/tokenStore` but the folder is `authentication/`. `ProtectedRoute.jsx` imports `./AuthContext` but the file is `AuthContect.jsx`. `autnEvent` is exported but `authEvents` is used. Event `"expied"` is dispatched but `"expired"` is listened for. Variable `erroe`. | n/a | Typos that stop the auth flow from running. |
| Lawyer login | The prototype accepts "email or Bar ID" | Email only | Use email, or extend SYS-19 to accept `bar_council_no`. |

The frontend on `lawyer_docupload_verify_badge` (Ahnaf's) already matches the verification endpoints. Two notes:
- **Document preview is metadata only.** The admin portal doesn't fetch the decrypted file yet (`getDocumentViewUrl` is unused). When it does, it must send the bearer header (see Private files above).
- **Fallback token.** It falls back to the token `demo_admin_token`, which will always get 401 against the real API.

## Where implemented code differs from `db/schema.sql`

The implemented endpoints are documented as they behave. These field differences should be reconciled when the code moves to Usama's models. Until then, the planned endpoints use the schema's names.

| Implemented code (`lawyer_docupload_verify_badge`) | `db/schema.sql` |
|---|---|
| `specialization` (free-text string) | Practice areas via `lawyer_practice_areas` → `practice_areas` (`slug`, `name_en`, `name_bn`) |
| `formats` as a comma-separated string, e.g. `"video,audio,chat"` | `formats consultation_format[]` (an array) |
| `rejection_reason` on the lawyer profile | `rejection_reason` only on `lawyer_verification_documents` |
| Document fields `original_filename`, `file_size_bytes`, `sha256_checksum`, `mime_type` and a server `file_path` | `file_url` only |
| No `primary_court_id`, `latitude` or `longitude` on the lawyer profile | Present |
| Client profile fields `nid_number`, `emergency_contact` | `gender`, `date_of_birth`, `organization_name`, `division`, `district`, `address`, `created_by_lawyer_id` |
| A new lawyer's account gets `status = active` | The seed uses `pending_verification` for unverified lawyers |
| Approve and reject are not logged | `audit_logs` exists for critical actions (FR-37) |

## Decisions and assumptions

- **Branch code counts as "implemented".** `main` has only empty placeholder files apart from `db/`, so endpoints that exist only on a branch are marked `implemented` with `x-merged-to-main: false`.
- **Login and refresh follow Ahnaf's backend.** Both the backend (`/api/auth/token/`) and Saker's frontend (`/api/auth/login/`) implement login. The team rule says to follow the backend, so I did, and recorded the differences above.
- **Logout path from the frontend.** `/api/auth/logout/` keeps the path Saker's client already calls (no backend exists), but takes `{refresh}` because SimpleJWT logout needs the token.
- **`/api/auth/me/` added (planned).** The token has no `role` claim and the frontend needs the role right after login.
- **The verification status endpoint already exists.** The lawyer's "my verification status" is `GET /api/lawyers/me/`. Its `verification_status`, `rejection_reason`, `verification_badge` and `documents` already cover it, so I didn't add a duplicate.
- **Approve and reject stay as two POST endpoints.** That is how they are implemented (`.../approve/` and `.../reject/` with `rejection_reason`), so I kept them rather than a single PATCH.
- **Re-upload after rejection is a new planned endpoint.** Today documents can only be uploaded during registration, which gives a rejected lawyer no way to fix them. `POST /api/lawyers/me/verification-documents/` fills that gap. It is allowed only when the status is `rejected`.
- **Client registration mirrors the lawyer path and style.** `POST /api/auth/register/client/` uses the same `{status, message, ...}` response with no auto-login. Its fields come from `users` + `client_profiles`, not the implemented `ClientProfile` model.
- **Planned passwords need at least 8 characters.** The implemented lawyer registration accepts 6. I recommend raising it to 8 so both forms match.
- **Password reset avoids account enumeration.** `forgot` accepts `email` or `phone` (FR-5 allows SMS) and always returns 200. Tokens are single-use, last 30 minutes and are stored hashed in `password_reset_tokens`.
- **Error formats are DRF's defaults.** I didn't invent a custom error envelope, because the implemented views already return DRF shapes.
- **Planned lists use DRF `PageNumberPagination`.** It is configured in settings with `PAGE_SIZE = 10`. The implemented unpaginated lists are documented as they are.
- **Examples use seed data.** The seed's users, Bar Council numbers, cases and conversations are reused. The seed row named after a real teammate isn't used, and no NID numbers appear anywhere.
- **Planned modules get Jira keys but no owners.** Their tickets (SYS-23 to SYS-60) have no assignee, so `x-owner` is `unassigned`.
- **The appointment state machine comes from the schema.** I derived it from the `appointment_status` enum and the schema's triggers and functions (SRS 7.7), because no SRS file is in the repo. SYS-30 should confirm the exact transitions.
- **The payment callback has its own prefix.** It lives at `/api/payment-gateways/{method}/callback/` so it can't be confused with `/api/payments/{payment_id}/...`.
- **The trailing-slash lint rule is off.** `no-path-trailing-slash` is disabled in `redocly.yaml` because Django paths need the slash. The localhost server warning is also off, because there is no deployed URL yet.
- **Error codes are listed only where they can happen.** Public endpoints list 401 (a bad token sent anyway) and 404 but not 403. `GET /` is a plain Django view, so it has no 401.
- **Real-time chat is out of scope here.** Chat delivery over WebSocket isn't something OpenAPI 3.0 can describe. The REST endpoints cover history and sending, and the planned socket URL is noted in the Chat operation.
