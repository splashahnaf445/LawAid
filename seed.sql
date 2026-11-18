-- LawAid demo seed data
-- Run AFTER schema.sql:
-- psql -U postgres -d lawaid -v ON_ERROR_STOP=1 -f seed.sql
--
-- Demo login password for all seeded accounts: Demo@123
-- These are fictional records for development/testing only.

BEGIN;
SET search_path = lawaid, public;

-- ------------------------------------------------------------
-- 1. Reference data
-- ------------------------------------------------------------
INSERT INTO courts (name, court_type, district) VALUES
('Supreme Court of Bangladesh - Appellate Division', 'supreme_court', 'Dhaka'),
('Supreme Court of Bangladesh - High Court Division', 'supreme_court', 'Dhaka'),
('Dhaka District and Sessions Judge Court', 'district', 'Dhaka'),
('Chattogram District Judge Court', 'district', 'Chattogram'),
('Sylhet District Judge Court', 'district', 'Sylhet'),
('Dhaka Family Court', 'family', 'Dhaka'),
('Labour Court, Dhaka', 'tribunal', 'Dhaka'),
('Cyber Tribunal, Dhaka', 'special', 'Dhaka'),
('Narayanganj District Judge Court', 'district', 'Narayanganj'),
('Rajshahi District Judge Court', 'district', 'Rajshahi')
ON CONFLICT (name) DO NOTHING;

INSERT INTO practice_areas (slug, name_en, name_bn) VALUES
('civil', 'Civil Law', 'দেওয়ানি আইন'),
('criminal', 'Criminal Law', 'ফৌজদারি আইন'),
('family', 'Family Law', 'পারিবারিক আইন'),
('land', 'Land and Property', 'ভূমি ও সম্পত্তি'),
('corporate', 'Corporate Law', 'কর্পোরেট আইন'),
('labour', 'Labour and Employment', 'শ্রম ও কর্মসংস্থান'),
('tax', 'Taxation', 'কর আইন'),
('constitutional', 'Constitutional Law', 'সাংবিধানিক আইন'),
('cyber', 'Cyber Law', 'সাইবার আইন'),
('immigration', 'Immigration Law', 'অভিবাসন আইন'),
('intellectual-property', 'Intellectual Property', 'মেধাস্বত্ব আইন'),
('contract', 'Contract Law', 'চুক্তি আইন')
ON CONFLICT (slug) DO NOTHING;

-- ------------------------------------------------------------
-- 2. Users: 100 clients, 20 lawyers, 3 admins
-- ------------------------------------------------------------
INSERT INTO users
(role, full_name, email, phone, password_hash, preferred_language, status,
 email_verified_at, phone_verified_at, last_login_at)
SELECT
  'client'::user_role,
  (ARRAY['Ayesha Rahman','Tanvir Ahmed','Nusrat Jahan','Sabbir Hossain',
         'Farhana Islam','Mehedi Hasan','Samira Akter','Rafiul Karim',
         'Tasnim Chowdhury','Imran Kabir','Maliha Sultana','Shakib Mahmud',
         'Nabila Noor','Arif Hossain','Sadia Afrin','Fahim Rahman'])[1 + ((g-1) % 16)]
       || ' ' || g,
  'client' || g || '@demo.lawaid.test',
  '+8801' || (3 + ((g-1) % 7))::text || lpad((10000000 + g)::text, 8, '0'),
  crypt('Demo@123', gen_salt('bf')),
  CASE WHEN g % 4 = 0 THEN 'en'::language_code ELSE 'bn'::language_code END,
  CASE WHEN g % 23 = 0 THEN 'suspended'::account_status ELSE 'active'::account_status END,
  now() - ((g % 90) || ' days')::interval,
  now() - ((g % 80) || ' days')::interval,
  now() - ((g % 14) || ' days')::interval
FROM generate_series(1,100) AS g
ON CONFLICT (email) DO NOTHING;

INSERT INTO users
(role, full_name, email, phone, password_hash, preferred_language, status,
 email_verified_at, phone_verified_at, last_login_at)
SELECT
  'lawyer'::user_role,
  (ARRAY['Adv. Mahmudul Hasan','Adv. Nusrat Sultana','Adv. Farid Ahmed',
         'Adv. Sharmin Akter','Adv. Rezaul Karim','Adv. Tanjim Rahman',
         'Adv. Samia Chowdhury','Adv. Kamrul Islam','Adv. Faria Haque',
         'Adv. Saifur Rahman'])[1 + ((g-1) % 10)] || ' ' || g,
  'lawyer' || g || '@demo.lawaid.test',
  '+8801' || (3 + ((g-1) % 7))::text || lpad((20000000 + g)::text, 8, '0'),
  crypt('Demo@123', gen_salt('bf')),
  CASE WHEN g % 3 = 0 THEN 'en'::language_code ELSE 'bn'::language_code END,
  'active'::account_status,
  now() - ((g % 120) || ' days')::interval,
  now() - ((g % 110) || ' days')::interval,
  now() - ((g % 10) || ' days')::interval
FROM generate_series(1,20) AS g
ON CONFLICT (email) DO NOTHING;

INSERT INTO users
(role, full_name, email, phone, password_hash, preferred_language, status,
 email_verified_at, phone_verified_at, last_login_at)
SELECT
  'admin'::user_role,
  (ARRAY['System Administrator','Platform Manager','Verification Officer'])[g],
  'admin' || g || '@demo.lawaid.test',
  '+8801' || (3 + g)::text || lpad((30000000 + g)::text, 8, '0'),
  crypt('Demo@123', gen_salt('bf')),
  'en', 'active', now(), now(), now() - ((g-1) || ' hours')::interval
FROM generate_series(1,3) AS g
ON CONFLICT (email) DO NOTHING;

-- ------------------------------------------------------------
-- 3. Client and lawyer profiles
-- ------------------------------------------------------------
INSERT INTO client_profiles (user_id, gender, date_of_birth, organization_name, division, district, address)
SELECT u.id,
       (ARRAY['male','female','other','undisclosed']::gender_type[])[1 + (row_number() OVER (ORDER BY u.email) % 4)],
       date '1980-01-01' + ((row_number() OVER (ORDER BY u.email)::int * 137) % 12000),
       CASE WHEN row_number() OVER (ORDER BY u.email) % 10 = 0
            THEN (ARRAY['Metro Housing Ltd.','Delta Trading Co.','Green Agro Limited','Northstar Technologies'])[1 + (row_number() OVER (ORDER BY u.email)::int % 4)]
            ELSE NULL END,
       (ARRAY['Dhaka','Chattogram','Rajshahi','Khulna','Sylhet','Barishal','Rangpur','Mymensingh'])[1 + ((row_number() OVER (ORDER BY u.email)::int - 1) % 8)],
       (ARRAY['Dhaka','Gazipur','Narayanganj','Chattogram','Cumilla','Rajshahi','Sylhet','Khulna'])[1 + ((row_number() OVER (ORDER BY u.email)::int - 1) % 8)],
       'House ' || (10 + row_number() OVER (ORDER BY u.email)::int) || ', Road ' || (1 + (row_number() OVER (ORDER BY u.email)::int % 20))
FROM users u
WHERE u.role = 'client'
  AND NOT EXISTS (SELECT 1 FROM client_profiles cp WHERE cp.user_id = u.id);

INSERT INTO lawyer_profiles
(user_id, honorific, headline, bar_council_no, bar_association, primary_court_id,
 chamber_address, district, latitude, longitude, years_experience, bio,
 consultation_fee, session_minutes, formats, offers_free_session, sos_available,
 verification_status, verified_at, verified_by)
SELECT u.id,
       'Adv.',
       (ARRAY['Senior Advocate','Advocate','Legal Consultant','Barrister-at-Law'])[1 + (n % 4)],
       'BD-DEMO-' || lpad(n::text, 5, '0'),
       (ARRAY['Dhaka Bar Association','Supreme Court Bar Association','Chattogram Bar Association','Sylhet Bar Association'])[1 + (n % 4)],
       (SELECT id FROM courts ORDER BY id OFFSET (n % (SELECT count(*) FROM courts)) LIMIT 1),
       'Chamber ' || (100+n) || ', Court Road, ' || (ARRAY['Dhaka','Chattogram','Sylhet','Rajshahi'])[1 + (n % 4)],
       (ARRAY['Dhaka','Chattogram','Sylhet','Rajshahi','Khulna'])[1 + (n % 5)],
       23.70 + (n * 0.013), 90.40 + (n * 0.017),
       2 + (n % 24),
       'Demo profile: experienced legal professional providing consultation and case assistance.',
       800 + (n * 250), 30 + (n % 3) * 15,
       CASE WHEN n % 3 = 0 THEN '{video,audio,chat}'::consultation_format[]
            WHEN n % 3 = 1 THEN '{audio,chat,in_person}'::consultation_format[]
            ELSE '{video,chat}'::consultation_format[] END,
       n % 5 = 0, n % 3 = 0,
       CASE WHEN n <= 15 THEN 'approved'::verification_status ELSE 'pending'::verification_status END,
       CASE WHEN n <= 15 THEN now() - ((n*3) || ' days')::interval ELSE NULL END,
       CASE WHEN n <= 15 THEN (SELECT id FROM users WHERE email='admin1@demo.lawaid.test') ELSE NULL END
FROM (
  SELECT u.id, row_number() OVER (ORDER BY u.email)::int AS n
  FROM users u
  WHERE u.role='lawyer'
    AND NOT EXISTS (SELECT 1 FROM lawyer_profiles lp WHERE lp.user_id=u.id)
) q
JOIN users u ON u.id=q.id;

INSERT INTO lawyer_practice_areas (lawyer_id, practice_area_id)
SELECT lp.user_id, pa.id
FROM lawyer_profiles lp
CROSS JOIN LATERAL (
  SELECT id FROM practice_areas
  ORDER BY md5(lp.bar_council_no || slug)
  LIMIT 2 + (right(lp.bar_council_no, 1)::int % 3)
) pa
ON CONFLICT DO NOTHING;

INSERT INTO lawyer_verification_documents (lawyer_id, doc_type, file_url, status, rejection_reason, reviewed_by, reviewed_at)
SELECT lp.user_id, d.doc_type,
       'https://demo.lawaid.test/private/verification/' || lp.bar_council_no || '/' || d.doc_type || '.pdf',
       CASE WHEN lp.verification_status='approved' THEN 'approved'::verification_status
            WHEN lp.verification_status='pending' THEN 'pending'::verification_status
            ELSE 'rejected'::verification_status END,
       NULL,
       CASE WHEN lp.verification_status='approved' THEN (SELECT id FROM users WHERE email='admin1@demo.lawaid.test') ELSE NULL END,
       CASE WHEN lp.verification_status='approved' THEN now() - interval '5 days' ELSE NULL END
FROM lawyer_profiles lp
CROSS JOIN (VALUES ('nid'::verification_doc), ('bar_certificate'::verification_doc)) d(doc_type)
WHERE NOT EXISTS (
  SELECT 1 FROM lawyer_verification_documents x
  WHERE x.lawyer_id=lp.user_id AND x.doc_type=d.doc_type
);

-- ------------------------------------------------------------
-- 4. Lawyer availability: 12 non-overlapping future slots/lawyer
-- ------------------------------------------------------------
INSERT INTO lawyer_availability_slots (lawyer_id, starts_at, ends_at, formats)
SELECT lp.user_id,
       date_trunc('day', now()) + ((g + 1) || ' days')::interval + interval '10 hours'
         + ((g % 3) * interval '2 hours'),
       date_trunc('day', now()) + ((g + 1) || ' days')::interval + interval '11 hours'
         + ((g % 3) * interval '2 hours'),
       lp.formats
FROM lawyer_profiles lp
CROSS JOIN generate_series(1,12) g
WHERE lp.verification_status='approved'
  AND NOT EXISTS (
    SELECT 1 FROM lawyer_availability_slots s
    WHERE s.lawyer_id=lp.user_id
      AND s.starts_at = date_trunc('day', now()) + ((g + 1) || ' days')::interval + interval '10 hours'
        + ((g % 3) * interval '2 hours')
  );

-- ------------------------------------------------------------
-- 5. Cases
-- ------------------------------------------------------------
INSERT INTO cases
(case_no, title, category, nature_tag, practice_area_id, court_id, bench, jurisdiction,
 lawyer_id, client_id, opposing_party, narrative, status, urgency, filed_at, stamp_fee_bdt)
SELECT
  'DEMO-' || to_char(current_date, 'YYYY') || '-' || lpad(g::text, 5, '0'),
  (ARRAY[
    'Rahman vs. Karim - Property Dispute',
    'ABC Traders vs. City Corporation',
    'State vs. Hasan - Criminal Matter',
    'Ayesha Rahman - Family Petition',
    'Delta Holdings vs. Green Developers',
    'Employment Dispute - Service Benefits',
    'Writ Petition concerning administrative action',
    'Contract Enforcement and Recovery Suit'
  ])[1 + ((g-1) % 8)] || ' #' || g,
  (ARRAY['Civil Suit','Writ Petition','Family Suit','Criminal Case','Arbitration','Labour Dispute'])[1 + ((g-1) % 6)],
  (ARRAY['LAND DISPUTE','CONTRACT','FAMILY MATTER','CRIMINAL DEFENCE','EMPLOYMENT','CONSTITUTIONAL'])[1 + ((g-1) % 6)],
  (SELECT id FROM practice_areas ORDER BY id OFFSET ((g-1) % (SELECT count(*) FROM practice_areas)) LIMIT 1),
  (SELECT id FROM courts ORDER BY id OFFSET ((g-1) % (SELECT count(*) FROM courts)) LIMIT 1),
  'Bench ' || (1 + (g % 12)),
  (ARRAY['Dhaka','Chattogram','Sylhet','Rajshahi','Khulna'])[1 + (g % 5)],
  l.user_id, c.user_id,
  (ARRAY['M/S Eastern Properties Ltd.','City Corporation','State','Former Employer Ltd.','Unknown Defendant'])[1 + (g % 5)],
  'Fictional demonstration case narrative for testing the LawAid case-management workflow.',
  (ARRAY['open','in_progress','pending_review','disposed','closed']::case_status[])[1 + ((g-1) % 5)],
  (ARRAY['regular','urgent','vacation_bench']::case_urgency[])[1 + ((g-1) % 3)],
  current_date - (g * 11),
  500 + (g * 25)
FROM generate_series(1,100) g
JOIN LATERAL (
  SELECT user_id, row_number() OVER (ORDER BY bar_council_no)::int AS rn
  FROM lawyer_profiles WHERE verification_status='approved'
) l ON l.rn = 1 + ((g-1) % 15)
JOIN LATERAL (
  SELECT user_id, row_number() OVER (ORDER BY id)::int AS rn
  FROM client_profiles
) c ON c.rn = 1 + ((g-1) % (SELECT count(*) FROM client_profiles))
ON CONFLICT (case_no) DO NOTHING;

-- ------------------------------------------------------------
-- 6. Appointments: 180 appointments linked to distinct slots
-- ------------------------------------------------------------
WITH slot_rows AS (
  SELECT s.id AS slot_id, s.lawyer_id, s.starts_at, s.ends_at,
         row_number() OVER (ORDER BY s.starts_at, s.lawyer_id)::int AS n
  FROM lawyer_availability_slots s
  JOIN lawyer_profiles lp ON lp.user_id=s.lawyer_id
  WHERE lp.verification_status='approved'
),
client_rows AS (
  SELECT user_id, row_number() OVER (ORDER BY user_id)::int AS n FROM client_profiles
),
case_rows AS (
  SELECT id, lawyer_id, client_id, row_number() OVER (ORDER BY case_no)::int AS n FROM cases
)
INSERT INTO appointments
(client_id, lawyer_id, slot_id, case_id, practice_area_id, format, status,
 scheduled_start, scheduled_end, issue_summary, fee_amount, is_sos, ai_recommended, hold_expires_at)
SELECT
  cr.user_id, sr.lawyer_id, sr.slot_id,
  (SELECT c.id FROM case_rows c
    WHERE c.lawyer_id=sr.lawyer_id AND c.client_id=cr.user_id
    ORDER BY c.n LIMIT 1),
  (SELECT practice_area_id FROM cases c
    WHERE c.lawyer_id=sr.lawyer_id AND c.client_id=cr.user_id
    ORDER BY c.created_at DESC LIMIT 1),
  (ARRAY['video','audio','chat','in_person']::consultation_format[])[1 + (sr.n % 4)],
  CASE WHEN sr.n % 10 = 0 THEN 'cancelled'::appointment_status
       WHEN sr.n % 7 = 0 THEN 'awaiting_lawyer'::appointment_status
       WHEN sr.n % 5 = 0 THEN 'confirmed'::appointment_status
       WHEN sr.n % 4 = 0 THEN 'payment_released'::appointment_status
       ELSE 'completed'::appointment_status END,
  sr.starts_at, sr.ends_at,
  (ARRAY['Property documentation review','Family legal consultation','Employment contract advice',
         'Business agreement review','Civil dispute consultation','General legal guidance'])[1 + (sr.n % 6)],
  CASE WHEN sr.n % 9 = 0 THEN 0 ELSE 1000 + (sr.n % 12) * 250 END,
  sr.n % 17 = 0, sr.n % 3 = 0,
  CASE WHEN sr.n % 10 = 0 THEN now() + interval '30 minutes' ELSE NULL END
FROM slot_rows sr
JOIN client_rows cr ON cr.n = 1 + ((sr.n-1) % (SELECT count(*) FROM client_rows))
WHERE sr.n <= 180
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 7. Appointment sessions, status history, payments and receipts
-- ------------------------------------------------------------
INSERT INTO consultation_sessions (appointment_id, room_id, started_at, ended_at, lawyer_notes)
SELECT a.id, 'demo-room-' || substr(a.id::text,1,12),
       a.scheduled_start, a.scheduled_start + interval '25 minutes',
       'Demo session notes: consultation completed and follow-up points recorded.'
FROM appointments a
WHERE a.status IN ('completed','payment_released')
  AND NOT EXISTS (SELECT 1 FROM consultation_sessions cs WHERE cs.appointment_id=a.id);

INSERT INTO payments
(appointment_id, client_id, lawyer_id, amount, platform_fee, method, gateway_txn_id,
 gateway_payload, status, escrow, paid_at, escrow_released_at)
SELECT a.id, a.client_id, a.lawyer_id,
       GREATEST(a.fee_amount, 500),
       round(GREATEST(a.fee_amount,500) * 0.10, 2),
       (ARRAY['sslcommerz','bkash','nagad']::payment_method[])[1 + (row_number() OVER (ORDER BY a.created_at)::int % 3)],
       'DEMO-TXN-' || substr(a.id::text,1,18),
       jsonb_build_object('demo', true, 'gateway', 'sandbox', 'currency', 'BDT'),
       'succeeded',
       CASE WHEN a.status='payment_released' THEN 'released'::escrow_status ELSE 'held'::escrow_status END,
       a.scheduled_start + interval '1 hour',
       CASE WHEN a.status='payment_released' THEN a.scheduled_start + interval '2 days' ELSE NULL END
FROM appointments a
WHERE a.status IN ('completed','payment_released')
  AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.appointment_id=a.id)
ON CONFLICT DO NOTHING;

INSERT INTO receipts (payment_id)
SELECT p.id FROM payments p
WHERE p.status='succeeded'
  AND NOT EXISTS (SELECT 1 FROM receipts r WHERE r.payment_id=p.id);

INSERT INTO reviews (appointment_id, client_id, lawyer_id, rating, comment, created_at)
SELECT a.id, a.client_id, a.lawyer_id,
       (ARRAY[3,4,5,5,4,5,2,4,5,3])[1 + (row_number() OVER (ORDER BY a.created_at)::int % 10)],
       (ARRAY['Very helpful and professional consultation.',
              'Clear explanation of the legal options.',
              'Good communication and timely guidance.',
              'The consultation was informative.',
              'Helpful discussion and practical next steps.'])[1 + (row_number() OVER (ORDER BY a.created_at)::int % 5)],
       a.scheduled_start + interval '1 day'
FROM appointments a
WHERE a.status IN ('completed','payment_released')
  AND NOT EXISTS (SELECT 1 FROM reviews r WHERE r.appointment_id=a.id)
ORDER BY a.created_at
LIMIT 70;

-- ------------------------------------------------------------
-- 8. Hearings, case team, updates and documents
-- ------------------------------------------------------------
INSERT INTO case_hearings (case_id, hearing_at, bench, courtroom, cause_list_item, purpose, status, outcome)
SELECT c.id,
       now() + ((g % 45 + 1) || ' days')::interval,
       c.bench, 'Courtroom ' || (1 + (g % 8)), 10 + g,
       (ARRAY['Initial hearing','Hearing on application','Evidence hearing','Final arguments','Mentioning'])[1 + (g % 5)],
       'scheduled', NULL
FROM cases c
JOIN LATERAL (SELECT row_number() OVER (ORDER BY case_no)::int AS n FROM cases x WHERE x.id=c.id) z ON true
CROSS JOIN generate_series(1,1) g
WHERE NOT EXISTS (SELECT 1 FROM case_hearings h WHERE h.case_id=c.id);

INSERT INTO case_team_members (case_id, user_id, team_role)
SELECT c.id, c.lawyer_id, 'Lead Counsel' FROM cases c
ON CONFLICT DO NOTHING;

INSERT INTO case_updates (case_id, author_id, message, is_client_visible, created_at)
SELECT c.id, c.lawyer_id,
       (ARRAY['Case file reviewed and initial strategy recorded.',
              'Relevant documents have been organized for review.',
              'The next hearing date has been added to the case timeline.',
              'A procedural update has been recorded for the client.',
              'The legal team has completed the latest case review.'])[1 + (row_number() OVER (ORDER BY c.case_no)::int % 5)],
       true, now() - ((row_number() OVER (ORDER BY c.case_no)::int % 30) || ' days')::interval
FROM cases c;

INSERT INTO case_documents
(case_id, uploaded_by, title, category, filed_by_party, file_url, mime_type, size_bytes,
 page_count, status, verified_by, verified_at, review_note, is_encrypted)
SELECT c.id, c.lawyer_id,
       (ARRAY['Case Petition','Supporting Affidavit','Written Statement','Evidence Bundle','Power of Attorney'])[1 + (row_number() OVER (ORDER BY c.case_no)::int % 5)],
       (ARRAY['Plaint','Affidavit','Written Statement','Exhibit','Other'])[1 + (row_number() OVER (ORDER BY c.case_no)::int % 5)],
       'Client',
       'https://demo.lawaid.test/private/cases/' || c.case_no || '/document-' || row_number() OVER (ORDER BY c.case_no) || '.pdf',
       'application/pdf', 120000 + (row_number() OVER (ORDER BY c.case_no)::int * 1700),
       2 + (row_number() OVER (ORDER BY c.case_no)::int % 28),
       (ARRAY['pending_review','verified','action_required','rejected']::document_status[])[1 + (row_number() OVER (ORDER BY c.case_no)::int % 4)],
       CASE WHEN row_number() OVER (ORDER BY c.case_no)::int % 4 = 1
            THEN (SELECT id FROM users WHERE email='admin1@demo.lawaid.test') ELSE NULL END,
       CASE WHEN row_number() OVER (ORDER BY c.case_no)::int % 4 = 1 THEN now() - interval '2 days' ELSE NULL END,
       NULL, true
FROM cases c;

-- ------------------------------------------------------------
-- 9. Lawyer tasks, calendar events and document requests
-- ------------------------------------------------------------
INSERT INTO tasks (lawyer_id, assignee_id, case_id, title, priority, status, due_at, completed_at)
SELECT c.lawyer_id, c.lawyer_id, c.id,
       (ARRAY['Review case documents','Prepare hearing notes','Contact client for details',
              'Draft legal submission','Check filing deadline','Prepare consultation summary'])[1 + (g % 6)],
       (ARRAY['urgent','medium','normal']::task_priority[])[1 + (g % 3)],
       CASE WHEN g % 5 = 0 THEN 'done'::task_status ELSE 'open'::task_status END,
       now() + ((g % 20 + 1) || ' days')::interval,
       CASE WHEN g % 5 = 0 THEN now() - interval '1 day' ELSE NULL END
FROM cases c
CROSS JOIN generate_series(1,2) g;

INSERT INTO calendar_events (lawyer_id, event_type, title, location, case_id, starts_at, ends_at, reminder_minutes_before)
SELECT c.lawyer_id,
       (ARRAY['court_hearing','chamber_review','virtual_review','filing_deadline']::event_type[])[1 + (g % 4)],
       (ARRAY['Court hearing','Chamber case review','Virtual client review','Filing deadline'])[1 + (g % 4)],
       c.jurisdiction, c.id,
       now() + ((g + 2) || ' days')::interval + interval '11 hours',
       now() + ((g + 2) || ' days')::interval + interval '12 hours',
       30
FROM cases c
CROSS JOIN generate_series(1,1) g;

WITH numbered_cases AS (
  SELECT c.*, row_number() OVER (ORDER BY c.case_no)::int AS rn
  FROM cases c
)
INSERT INTO document_requests
(requested_by, recipient_type, recipient_user_id, recipient_name, case_id, status, due_at, channels)
SELECT c.lawyer_id, 'client', c.client_id,
       u.full_name, c.id,
       (ARRAY['sent','partially_fulfilled','fulfilled']::request_status[])[1 + (c.rn % 3)],
       now() + interval '7 days', '{sms,whatsapp,email}'::notif_channel[]
FROM numbered_cases c
JOIN users u ON u.id=c.client_id
WHERE c.rn <= 60;

INSERT INTO document_request_items (request_id, label, priority)
SELECT dr.id, item.label, item.priority
FROM document_requests dr
CROSS JOIN (VALUES
  ('National ID copy','MANDATORY'),
  ('Relevant agreement or contract','STANDARD'),
  ('Supporting evidence','URGENT')
) AS item(label, priority);

-- ------------------------------------------------------------
-- 10. Conversations and messages
-- ------------------------------------------------------------
INSERT INTO conversations (client_id, lawyer_id, case_id, created_at)
SELECT DISTINCT c.client_id, c.lawyer_id, c.id, now() - interval '10 days'
FROM cases c
WHERE NOT EXISTS (
  SELECT 1 FROM conversations cv
  WHERE cv.client_id=c.client_id AND cv.lawyer_id=c.lawyer_id AND cv.case_id=c.id
);

INSERT INTO messages (conversation_id, sender_id, msg_type, body, sent_at, read_at)
SELECT cv.id, cv.client_id, 'text',
       'Hello, I would like an update about my case and the next steps.',
       now() - interval '2 days', now() - interval '1 day'
FROM conversations cv;

INSERT INTO messages (conversation_id, sender_id, msg_type, body, sent_at, read_at)
SELECT cv.id, cv.lawyer_id, 'text',
       'Thank you for reaching out. I have reviewed the latest documents and will share an update shortly.',
       now() - interval '1 day', NULL
FROM conversations cv;

-- ------------------------------------------------------------
-- 11. SOS requests
-- ------------------------------------------------------------
INSERT INTO sos_requests (client_id, description, latitude, longitude, status, lawyer_id, requested_at, accepted_at)
SELECT cp.user_id,
       (ARRAY['Urgent assistance required for a property matter.',
              'Need immediate legal guidance regarding an employment issue.',
              'Requesting urgent consultation about a family matter.'])[1 + (g % 3)],
       23.70 + (g * 0.009), 90.40 + (g * 0.011),
       (ARRAY['requested','matched','accepted','completed']::sos_status[])[1 + (g % 4)],
       CASE WHEN g % 4 = 0 THEN NULL
            ELSE (SELECT user_id FROM lawyer_profiles WHERE verification_status='approved' ORDER BY bar_council_no OFFSET (g % 15) LIMIT 1) END,
       now() - ((g % 12) || ' hours')::interval,
       CASE WHEN g % 4 IN (2,3) THEN now() - ((g % 8) || ' hours')::interval ELSE NULL END
FROM (SELECT user_id, row_number() OVER (ORDER BY user_id)::int AS n FROM client_profiles) cp
JOIN generate_series(1,30) g ON g = cp.n;

-- ------------------------------------------------------------
-- 12. Confidential reports and attachments
-- ------------------------------------------------------------
INSERT INTO confidential_reports
(reporter_id, is_anonymous, lawyer_id, lawyer_name_text, violation_type, statement,
 status, admin_notes, handled_by, resolved_at)
SELECT
  CASE WHEN g % 5 = 0 THEN NULL ELSE cp.user_id END,
  g % 5 = 0,
  lp.user_id, NULL,
  (ARRAY['Professional misconduct','Unethical billing','Communication concern',
         'Conflict of interest','Confidentiality concern'])[1 + (g % 5)],
  'Fictional confidential report #' || g || ' submitted as sample data for admin review testing.',
  (ARRAY['submitted','under_review','action_taken','dismissed']::report_status[])[1 + (g % 4)],
  CASE WHEN g % 4 IN (2,3) THEN 'Demo administrative review note.' ELSE NULL END,
  CASE WHEN g % 4 IN (2,3) THEN (SELECT id FROM users WHERE email='admin2@demo.lawaid.test') ELSE NULL END,
  CASE WHEN g % 4 IN (2,3) THEN now() - interval '1 day' ELSE NULL END
FROM generate_series(1,20) g
JOIN LATERAL (SELECT user_id FROM client_profiles ORDER BY user_id OFFSET ((g-1) % (SELECT count(*) FROM client_profiles)) LIMIT 1) cp ON true
JOIN LATERAL (SELECT user_id FROM lawyer_profiles ORDER BY user_id OFFSET ((g-1) % (SELECT count(*) FROM lawyer_profiles)) LIMIT 1) lp ON true;

INSERT INTO confidential_report_attachments (report_id, file_url, file_name)
SELECT id, 'https://demo.lawaid.test/private/reports/' || id::text || '/supporting-document.pdf',
       'supporting-document.pdf'
FROM confidential_reports
WHERE is_anonymous = false;

-- ------------------------------------------------------------
-- 13. AI conversations, messages and recommendations
-- ------------------------------------------------------------
INSERT INTO ai_conversations (user_id, session_token, language, title, module, created_at)
SELECT cp.user_id, NULL,
       CASE WHEN g % 3 = 0 THEN 'en'::language_code ELSE 'bn'::language_code END,
       (ARRAY['Understanding land registration','Tenant rights and obligations',
              'Family law general guidance','Employment contract questions',
              'How to prepare for a civil case','Basic legal procedure in Bangladesh'])[1 + (g % 6)],
       (ARRAY['General Legal Questions','Land and Property','Family Law',
              'Employment Law','Civil Procedure'])[1 + (g % 5)],
       now() - ((g % 20) || ' days')::interval
FROM generate_series(1,60) g
JOIN LATERAL (SELECT user_id FROM client_profiles ORDER BY user_id OFFSET ((g-1) % (SELECT count(*) FROM client_profiles)) LIMIT 1) cp ON true;

INSERT INTO ai_messages
(conversation_id, role, content, language, model, prompt_tokens, completion_tokens,
 is_out_of_scope, disclaimer_shown, citations, flagged_for_review)
SELECT ac.id, 'user',
       'I need general information about the legal process for my issue. This is a demo question.',
       ac.language, 'demo-assistant', 35, 0, false, false, NULL, false
FROM ai_conversations ac;

INSERT INTO ai_messages
(conversation_id, role, content, language, model, prompt_tokens, completion_tokens,
 is_out_of_scope, disclaimer_shown, citations, flagged_for_review)
SELECT ac.id, 'assistant',
       'This is a demonstration response, not legal advice. Please consult a qualified lawyer for advice about your specific circumstances.',
       ac.language, 'demo-assistant', 0, 45, false, true,
       '[{"act":"Demo Legal Reference","section":"Sample section"}]'::jsonb,
       ac.id::text LIKE '%a%a%a%'
FROM ai_conversations ac;

INSERT INTO ai_recommendations (client_id, issue_text, filters)
SELECT cp.user_id,
       'Need a lawyer for a property or civil dispute.',
       jsonb_build_object('district', 'Dhaka', 'language', 'bn', 'demo', true)
FROM client_profiles cp
ORDER BY cp.user_id
LIMIT 25;

INSERT INTO ai_recommendation_items (recommendation_id, lawyer_id, rank, score, reason)
SELECT ar.id, lp.user_id,
       row_number() OVER (PARTITION BY ar.id ORDER BY lp.avg_rating DESC, lp.consultation_fee)::smallint,
       round((0.95 - (row_number() OVER (PARTITION BY ar.id ORDER BY lp.avg_rating DESC, lp.consultation_fee) * 0.035))::numeric, 4),
       'Matched using practice area, location and profile rating (demo explanation).'
FROM ai_recommendations ar
CROSS JOIN LATERAL (
  SELECT user_id, avg_rating, consultation_fee
  FROM lawyer_profiles
  WHERE verification_status='approved'
  ORDER BY avg_rating DESC, consultation_fee
  LIMIT 5
) lp
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 14. Notifications, audit logs, CMS and settings
-- ------------------------------------------------------------
INSERT INTO notifications (user_id, channel, kind, title, body, entity_type, status, scheduled_for, sent_at, read_at)
SELECT u.id,
       (ARRAY['in_app','push','sms','whatsapp','email']::notif_channel[])[1 + (g % 5)],
       (ARRAY['appointment_reminder','hearing_reminder','payment_due','verification','case_update'])[1 + (g % 5)],
       (ARRAY['Appointment reminder','Upcoming hearing','Payment update','Profile verification','Case update'])[1 + (g % 5)],
       'This is a sample LawAid notification for dashboard and notification-center testing.',
       'demo', (ARRAY['queued','sent','read','failed']::notif_status[])[1 + (g % 4)],
       now() + ((g % 5) || ' hours')::interval,
       CASE WHEN g % 4 <> 0 THEN now() - interval '1 hour' ELSE NULL END,
       CASE WHEN g % 4 = 3 THEN now() - interval '30 minutes' ELSE NULL END
FROM users u
CROSS JOIN generate_series(1,2) g;

INSERT INTO audit_logs (actor_id, actor_role, action, entity_type, entity_id, ip_address, metadata, created_at)
SELECT u.id, u.role,
       (ARRAY['auth.login','profile.update','appointment.create','case.update',
              'document.upload','payment.succeeded','verification.review'])[1 + (g % 7)],
       (ARRAY['user','appointment','case','document','payment','lawyer_profile'])[1 + (g % 6)],
       'DEMO-ENTITY-' || g,
       ('192.0.2.' || (1 + (g % 250)))::inet,
       jsonb_build_object('demo', true, 'source', 'seed.sql', 'sequence', g),
       now() - ((g % 60) || ' days')::interval
FROM users u
CROSS JOIN generate_series(1,3) g;

INSERT INTO content_items (slug, kind, title_en, title_bn, body_en, body_bn, is_published, author_id)
VALUES
('about-lawaid','policy','About LawAid','লঅ্যাইড সম্পর্কে',
 'LawAid is a demonstration legal assistance and law management platform.',
 'LawAid একটি প্রদর্শনীমূলক আইনি সহায়তা ও আইন ব্যবস্থাপনা প্ল্যাটফর্ম।', true,
 (SELECT id FROM users WHERE email='admin1@demo.lawaid.test')),
('booking-guide','legal_guide','How to Book a Consultation','পরামর্শ বুক করার নিয়ম',
 'Search for a verified lawyer, choose an available slot and submit a booking request.',
 'একজন যাচাইকৃত আইনজীবী খুঁজুন, সময় নির্বাচন করুন এবং বুকিং অনুরোধ পাঠান।', true,
 (SELECT id FROM users WHERE email='admin1@demo.lawaid.test')),
('payment-faq','faq','Payment and Escrow FAQ','পেমেন্ট ও এসক্রো FAQ',
 'Payments are represented with sandbox gateway references in this demo database.',
 'এই ডেমো ডেটাবেজে পেমেন্ট স্যান্ডবক্স গেটওয়ে রেফারেন্স দিয়ে দেখানো হয়েছে।', true,
 (SELECT id FROM users WHERE email='admin2@demo.lawaid.test')),
('privacy-policy','policy','Privacy and Confidentiality','গোপনীয়তা নীতি',
 'Demo content only. Production deployments must publish reviewed privacy terms.',
 'শুধুমাত্র ডেমো কনটেন্ট। প্রকৃত ব্যবহারের আগে নীতিমালা পর্যালোচনা করতে হবে।', false,
 (SELECT id FROM users WHERE email='admin3@demo.lawaid.test'))
ON CONFLICT (slug) DO NOTHING;

INSERT INTO system_settings (key, value, description, updated_by)
VALUES
('platform_name', '"LawAid"', 'Platform display name', (SELECT id FROM users WHERE email='admin1@demo.lawaid.test')),
('default_language', '"bn"', 'Default interface language', (SELECT id FROM users WHERE email='admin1@demo.lawaid.test')),
('platform_fee_percent', '10', 'Demo platform fee percentage', (SELECT id FROM users WHERE email='admin2@demo.lawaid.test')),
('booking_hold_minutes', '15', 'Minutes to hold a booking during payment', (SELECT id FROM users WHERE email='admin2@demo.lawaid.test')),
('demo_mode', 'true', 'Indicates that seeded records are fictional demo data', (SELECT id FROM users WHERE email='admin3@demo.lawaid.test'))
ON CONFLICT (key) DO UPDATE
SET value=EXCLUDED.value, description=EXCLUDED.description, updated_at=now();

COMMIT;

-- Quick verification counts
SELECT 'users' AS table_name, count(*) AS rows FROM lawaid.users
UNION ALL SELECT 'client_profiles', count(*) FROM lawaid.client_profiles
UNION ALL SELECT 'lawyer_profiles', count(*) FROM lawaid.lawyer_profiles
UNION ALL SELECT 'cases', count(*) FROM lawaid.cases
UNION ALL SELECT 'appointments', count(*) FROM lawaid.appointments
UNION ALL SELECT 'payments', count(*) FROM lawaid.payments
UNION ALL SELECT 'reviews', count(*) FROM lawaid.reviews
UNION ALL SELECT 'messages', count(*) FROM lawaid.messages
UNION ALL SELECT 'notifications', count(*) FROM lawaid.notifications;
