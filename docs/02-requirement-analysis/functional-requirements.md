# Functional Requirements (FR-1 to FR-40)

Every requirement traces back to the benchmark or the survey.

## User Registration & Verification
| ID | Requirement |
|---|---|
| FR-1 | Register as a **Client** or **Lawyer** with separate flows |
| FR-2 | Lawyers upload a valid **NID** and **Bar Council certificate** for verification |
| FR-3 | Show a **verification badge** only after NID and certificate are reviewed and approved |
| FR-4 | Secure login with **JWT-based authentication** |
| FR-5 | Secure password recovery |

## Lawyer Search & AI Matching
| ID | Requirement |
|---|---|
| FR-6 | Search lawyers by **specialization, location, rating and fee** |
| FR-7 | **AI-powered recommendations** from the client's stated legal issue and criteria |
| FR-8 | Lawyer profile shows specialization, verification status, ratings, reviews and fees |
| FR-9 | View and sort results by rating, price or relevance |

## Appointment Booking & Consultation
| ID | Requirement |
|---|---|
| FR-10 | Book a **free or paid** appointment |
| FR-11 | Choose **video, audio, real-time chat or in-person** consultation |
| FR-12 | See available slots and confirm one without phone calls or back-and-forth |
| FR-13 | Lawyers can accept, reschedule or decline requests |
| FR-14 | Live **video/audio calling and real-time chat** inside the platform |
| FR-15 | Automated **reminders** (push and SMS) for appointments, hearings and payment due dates |
| FR-16 | **24/7 emergency lawyer finder (SOS)** for urgent situations |

## Case Management
| ID | Requirement |
|---|---|
| FR-17 | **Case-management dashboard** for lawyers and clients |
| FR-18 | Lawyers log and track **court hearing dates** |
| FR-19 | Upload, store and retrieve **case documents** |
| FR-20 | Lawyers update case status (open, in progress, closed), visible to the client |

## Payments & Verification
| ID | Requirement |
|---|---|
| FR-21 | Secure online payments via **SSLCommerz, bKash and Nagad** |
| FR-22 | **Escrow**: funds released only after the consultation is confirmed complete |
| FR-23 | **QR-verified digital receipt** for every payment |
| FR-24 | View payment history and download receipts |
| FR-25 | **Dispute a transaction** if service was not delivered |

## Bilingual AI Legal Assistant
| ID | Requirement |
|---|---|
| FR-26 | **Free, public** AI chatbot, no paid consultation required |
| FR-27 | Responds in **Bangla and English** |
| FR-28 | Explains basic laws, citizens' rights and consequences in plain language |
| FR-29 | Scoped to **general information only**, prompting users to book a verified lawyer for case-specific advice |

## Ratings, Reviews & Trust
| ID | Requirement |
|---|---|
| FR-30 | **Rate and review** a lawyer after a completed consultation |
| FR-31 | Show average rating and review count on public profiles |
| FR-32 | Submit a **confidential report** about unethical conduct |
| FR-33 | Route confidential reports to administrators only, never public |

## Notifications & Security
| ID | Requirement |
|---|---|
| FR-34 | **Role-based access control** for client, lawyer and admin |
| FR-35 | **End-to-end encryption** of case documents and payment information |
| FR-36 | **Push and SMS alerts** for appointments, hearings and deadlines |
| FR-37 | Audit log for critical actions (bookings, payments, uploads) |

## Administration
| ID | Requirement |
|---|---|
| FR-38 | Admin panel to **approve or reject** lawyer verification submissions |
| FR-39 | Admins can **suspend or remove** accounts violating policy |
| FR-40 | Admins review confidential misconduct reports and act |
