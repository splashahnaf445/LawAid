# Non-Functional Requirements (NFR-1 to NFR-22)

## Security
| ID | Requirement |
|---|---|
| NFR-1 | End-to-end encryption of case documents, personal ID and payment data, in transit and at rest |
| NFR-2 | Role-based access control for clients, lawyers and admins |
| NFR-3 | JWT session authentication with expiry and refresh handling |
| NFR-4 | NID and Bar Council documents visible only to administrators during verification |
| NFR-5 | Payments via PCI-compliant gateways (SSLCommerz, bKash, Nagad); no raw card/account data stored on LawAid servers |

## Privacy
| ID | Requirement |
|---|---|
| NFR-6 | Comply with a clearly published data privacy policy |
| NFR-7 | Confidential misconduct reports visible only to admins |
| NFR-8 | Users can request deletion of their personal data |

## Usability
| ID | Requirement |
|---|---|
| NFR-9 | Mobile-first, intuitive interface (most respondents are 18-34) |
| NFR-10 | Full bilingual (Bangla/English) support across all screens |
| NFR-11 | Inclusive, gender-balanced interface design |
| NFR-12 | Lawyer search and booking in a minimal number of steps |

## Performance
| ID | Requirement |
|---|---|
| NFR-13 | Search results and profiles load within 2-3 seconds |
| NFR-14 | Low-latency real-time video, audio and chat |
| NFR-15 | AI chatbot responds within a few seconds under typical load |

## Reliability & Availability
| ID | Requirement |
|---|---|
| NFR-16 | 24/7 availability, especially for the SOS feature |
| NFR-17 | Payment/booking integrity: never charged without a confirmed booking, and vice versa |
| NFR-18 | Reliable retention and backup of case documents |

## Scalability
| ID | Requirement |
|---|---|
| NFR-19 | Scale lawyer and client base without significant degradation |
| NFR-20 | Add payment methods and languages without major rework |

## Maintainability
| ID | Requirement |
|---|---|
| NFR-21 | Modular architecture: separate services for search/matching, booking, payments, chatbot and case management |
| NFR-22 | Error and critical-action logging for debugging and audit |
