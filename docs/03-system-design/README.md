# 03 · System Design

> SDLC phase 3 of 6 · **Status: ✅ Complete**

| Folder / file | Contents |
|---|---|
| [`uml-diagrams/`](uml-diagrams) | Use case, activity, data flow, class, sequence, state diagrams and CRC cards |
| [`use-case-descriptions.md`](use-case-descriptions.md) | Fully specified descriptions of the 3 major use cases |
| [`ui-ux-prototype/`](ui-ux-prototype) | High-fidelity Figma prototype: 6 web and 7 mobile screens, design system, navigation flow |

## Architecture at a glance
Two-sided portal (Client app + Lawyer dashboard) plus an Admin panel, built from independent modules (NFR-21).

```mermaid
flowchart LR
    C[Client app<br/>web + mobile] --> API
    L[Lawyer dashboard] --> API
    A[Admin panel] --> API
    API[Backend API<br/>JWT + RBAC] --> M1[Search & AI matching]
    API --> M2[Appointment booking]
    API --> M3[Case management]
    API --> M4[Payments & escrow]
    API --> M5[Bilingual AI chatbot]
    API --> M6[Verification & moderation]
    M4 --> PG[SSLCommerz / bKash / Nagad]
    M5 --> AI[OpenAI / Gemini API]
    API --> DB[(PostgreSQL)]
```
