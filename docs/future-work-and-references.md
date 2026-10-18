# Conclusion, Future Work & References

## Conclusion
The SRS defines LawAid's objectives, scope, functional and non-functional requirements and design considerations. It addresses common challenges: difficulty finding suitable legal help, managing case information, and keeping communication between clients and lawyers. It is intended as a foundation for design, development, testing and enhancement.

## Future work
| Theme | Idea |
|---|---|
| **Grounded, verifiable AI assistant** | Retrieval-augmented generation (RAG) over an official corpus of Bangladeshi Acts, ordinances and gazettes. Answers cite the exact Act and section, and the assistant declines when the law does not cover a question. |
| **e-Judiciary integration** | Pull hearing dates and case status from official court systems into the case dashboard instead of manual entry. |
| **Free legal-aid referral** | Assess eligibility under the Legal Aid Services Act, 2000 and direct users to the nearest district legal aid office [3]. |
| **Low-bandwidth, voice and offline access** | Bangla voice input/output, lightweight mode for slow networks, SMS hearing alerts, and a possible offline small legal model. |
| **Legal document automation** | Guided templates (notices, affidavits, rental agreements, power of attorney), each reviewed by a verified lawyer and never presented as a replacement for legal advice [7]. |
| **Online dispute resolution** | Online mediation with certified mediators using the existing video, chat and payment features [1], [2]. |
| **Smarter, fairer matching** | Use outcome data, explain each recommendation, and audit rankings so new lawyers, female lawyers and lawyers outside Dhaka are not ranked unfairly lower. |
| **Full data-protection compliance** | Formal review against the Personal Data Protection Ordinance, 2025 before commercial launch [10]. |
| **Pilot deployment** | Pilot in one or two districts measuring task completion time, SUS satisfaction, booking completion rate and chatbot accuracy. |

## References
1. A. Sarkar, "Over 45 lakh cases pending in courts," *The Daily Star*, Jul. 6, 2025. https://www.thedailystar.net/news/bangladesh/news/over-45-lakh-cases-pending-courts-3933306
2. "Over 46 lakh cases pending across courts in Bangladesh: Law minister," *The Daily Star*, 2026. https://www.thedailystar.net/news/the-parliament-watch/parliament/news/over-46-lakh-cases-pending-across-courts-bangladesh-law-minister-4218096
3. Government of Bangladesh, *Legal Aid Services Act, 2000* (Act No. VI of 2000).
4. A. T. Wasi, W. Faisal, M. R. Islam, and M. M. Bappy, "Exploring possibilities of AI-powered legal assistance in Bangladesh through large language modeling," arXiv:2410.17210, 2024.
5. A. T. Wasi, W. Faisal, M. R. Islam, and M. R. Parvez, "Mina: A multilingual LLM-powered legal assistant agent for Bangladesh for empowering access to justice," arXiv:2511.08605, 2025.
6. S. Aftahee et al., "Assessing the reliability of large language models in the Bengali legal context: A comparative evaluation using LLM-as-judge and legal experts," arXiv:2511.05627, 2025.
7. Federal Trade Commission, "FTC finalizes order with DoNotPay that prohibits deceptive 'AI lawyer' claims," Feb. 2025.
8. M. Dahl, V. Magesh, M. Suzgun, and D. E. Ho, "Large legal fictions: Profiling legal hallucinations in large language models," *J. Legal Anal.*, vol. 16, no. 1, pp. 64-93, 2024, doi: 10.1093/jla/laae003.
9. V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, "Hallucination-free? Assessing the reliability of leading AI legal research tools," *J. Empir. Leg. Stud.*, vol. 22, no. 2, pp. 216-242, 2025, doi: 10.1111/jels.12413.
10. Government of Bangladesh, *Personal Data Protection Ordinance, 2025* (Ordinance No. 61 of 2025).
11. Government of Bangladesh, *Cyber Security Ordinance, 2025*.
12. Bangladesh Bar Council, *Canons of Professional Conduct and Etiquette*, under the Bangladesh Legal Practitioners and Bar Council Order, 1972.
