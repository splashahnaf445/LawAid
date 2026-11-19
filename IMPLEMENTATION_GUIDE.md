# LawAid — Lawyer Verification & Document Compliance Implementation

This directory contains the complete implementation for the two assigned SRS tasks for the **LawAid** platform:

1. **Task 1: Lawyer NID and Bar Council Certificate Upload (SRS: FR-2, NFR-4)**
   - *SRS FR-2:* Lawyers must upload their National ID (NID) and Bangladesh Bar Council certificate (Sanad) during registration.
   - *SRS NFR-4:* Uploaded identity documents are stored **encrypted at rest** and accessible **only to platform compliance administrators**. Raw documents are strictly hidden from clients, public users, and other lawyers.
2. **Task 2: Verification Status and Badge Logic (SRS: FR-3, FR-38)**
   - *SRS FR-3:* Show official verification badge on lawyer profile **only after admin approval**.
   - *SRS FR-3:* Lawyer is **strictly hidden from search results** until verified.
   - *SRS FR-38:* Platform administrators review pending submissions, inspect decrypted documents, and approve or reject submissions with reason tracking.

---

## Folder Architecture

The implementation is cleanly separated into two distinct folders as requested:

```
lawyer_verification_and_docs/
├── backend/                       # Backend (Django REST Framework + PostgreSQL/SQLite)
│   ├── config/                    # Django project configuration (settings, urls, wsgi)
│   ├── accounts/                  # Authentication, Verification & Lawyer Directory app
│   │   ├── models.py              # User, LawyerProfile, LawyerVerificationDocument models
│   │   ├── encryption.py          # Fernet AES-128-CBC + HMAC-SHA256 authenticated encryption service
│   │   ├── permissions.py         # IsPlatformAdmin & IsAdminOnlyForDocuments (strictly enforces NFR-4)
│   │   ├── validators.py          # Bangladesh phone (+8801...), Bar Council Sanad format, file format/size checks
│   │   ├── serializers.py         # Lawyer registration, verification document, search & badge serializers
│   │   ├── views.py               # Document upload, admin review queue, document decryption stream, approve/reject, search filter
│   │   ├── urls.py                # API routing endpoints
│   │   ├── admin.py               # Django Admin integration with badge renderers
│   │   ├── management/commands/   # seed_demo_data command to seed test accounts & encrypted docs
│   │   └── tests/                 # 11 automated unit & integration tests (100% pass)
│   │       ├── test_encryption.py
│   │       ├── test_access_control.py
│   │       ├── test_verification_workflow.py
│   │       └── test_search_badge_logic.py
│   ├── requirements.txt           # Python dependencies (django, djangorestframework, cryptography, etc.)
│   └── .env.example               # Environment variables configuration
│
└── frontend/                      # Frontend (React 19 + Vite + Tailwind/Lucide)
    ├── src/
    │   ├── components/
    │   │   ├── VerifiedBadge.jsx            # LawAid Verified Advocate badge with Sanad metadata tooltip
    │   │   ├── LawyerRegistration.jsx       # Registration form with NID & Bar Council upload dropzones (FR-2)
    │   │   ├── AdminVerificationPortal.jsx  # Admin queue, in-memory document decryption & approve/reject (FR-38, NFR-4)
    │   │   ├── LawyerDirectory.jsx          # Public search hiding unverified lawyers and displaying badges (FR-3)
    │   │   └── LawyerProfileModal.jsx       # Detailed profile modal with verification trust seal
    │   ├── services/
    │   │   └── api.js                       # Centralized API service client (with offline demo fallback)
    │   ├── App.jsx                          # Main portal interface with navigation tabs
    │   ├── main.jsx                         # React root entry
    │   └── index.css                        # LawAid design system styling
    ├── package.json                         # Node dependencies (vite, react, lucide-react)
    └── vite.config.js                       # Proxy configuration to Django backend (:8000)
```

---

## How It Solves the Requirements

### 1. Document Upload & AES Encryption (FR-2, NFR-4)
- **Encryption Service (`backend/accounts/encryption.py`):**
  - Files are encrypted before being written to disk using `cryptography.fernet.Fernet` (authenticated AES-128-CBC with HMAC-SHA256 message authentication).
  - Physical files stored on disk (`storage/encrypted_documents/*.enc`) contain purely unreadable ciphertext.
- **Admin-Only Decryption Endpoint (`backend/accounts/views.py`):**
  - Endpoint: `GET /api/verification/documents/<doc_id>/view/`
  - Access Control: Enforces `IsAdminOnlyForDocuments`.
  - Clients, unauthorized users, or competitors receive `403 Forbidden`.
  - When an authenticated admin requests a document, it is read and decrypted on-the-fly in server memory and streamed as a `FileResponse` with original MIME type. No plaintext file is ever written to disk or exposed over public URLs.

### 2. Verification Status & Badge Logic (FR-3)
- **Verification Lifecycle:**
  - Statuses: `pending`, `approved`, `rejected`.
  - When a lawyer registers, status is set to `pending`, `is_verified = False`, and `verification_badge = None`.
- **Search Filtering (Hidden until verified):**
  - `GET /api/lawyers/` strictly filters `verification_status = 'approved'`.
  - Pending and rejected lawyers are excluded from search results.
- **Verification Badge:**
  - Badge object is generated dynamically on lawyer profile and search results only when `verification_status == 'approved'`.
  - Includes official Bar Council Sanad number, bar association, verified timestamp, and LawAid verification seal.
- **Admin Review Actions (FR-38):**
  - `POST /api/verification/lawyers/<id>/approve/` -> Sets status to `approved`, stamps `verified_at` and `verified_by`, activates badge, and exposes lawyer in search.
  - `POST /api/verification/lawyers/<id>/reject/` -> Requires `rejection_reason`, sets status to `rejected`, keeps lawyer hidden and unbadged.

---

## How to Run & Test

### Running Backend (Django REST Framework)
```bash
cd backend
# 1. Activate venv
.\venv\Scripts\activate   # On Windows (or source venv/bin/activate on Linux/Mac)

# 2. Run automated tests (All 11 tests)
python manage.py test accounts

# 3. Seed demo data (creates admin and sample verified/pending lawyers)
python manage.py seed_demo_data

# 4. Start backend server
python manage.py runserver 127.0.0.1:8000
```

**Pre-seeded Demo Credentials:**
- **Lead Administrator:** `admin@lawaid.gov.bd` / Password: `LawAid@123`
- **Client Account:** `ahnaf@gmail.com` / Password: `LawAid@123`
- **Verified Lawyer 1:** `s.farhana@apexlegal.bd` / Password: `LawAid@123` (Bar ID: `SC-7841`)
- **Verified Lawyer 2:** `tanvir.ahmed@dhakabar.bd` / Password: `LawAid@123` (Bar ID: `DH-9124`)
- **Pending Lawyer (Hidden):** `m.hasan@legalchambers.bd` (Bar ID: `DH-4412`)

### Running Frontend (React)
```bash
cd frontend
# 1. Start development server
npm run dev

# 2. Open browser at:
# http://localhost:3000
```

---

## Git Push Options

Because the implementation is split into `backend/` and `frontend/`, you can push them based on your team's branch strategy:

### Option A: Push Backend to `feature/lawyer-verification-api` and Frontend to `feature/verification-and-admin-ui`
```bash
# Push backend branch
git checkout -b feature/lawyer-verification-api
git add backend/
git commit -m "feat(api): implement lawyer NID/Bar Sanad encryption and verification badge API [FR-2, FR-3, NFR-4]"
git push origin feature/lawyer-verification-api

# Push frontend branch
git checkout -b feature/verification-and-admin-ui
git add frontend/
git commit -m "feat(ui): implement lawyer registration upload, verified badge, and admin review portal"
git push origin feature/verification-and-admin-ui
```

### Option B: Push both together on your assigned branch `lawyer_verification_and_docs`
```bash
git add .
git commit -m "feat(verification): complete lawyer document encryption upload and badge verification logic [FR-2, FR-3, NFR-4]"
git push origin lawyer_verification_and_docs
```
