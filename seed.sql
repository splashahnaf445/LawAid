-- =====================================================================
--  LawAid  -  seed / demo data   (run AFTER schema.sql)
--  All demo accounts share the password:  LawAid@123
--  Dates are relative to now(), so the demo never goes stale.
-- =====================================================================
SET client_encoding = 'UTF8';
SET search_path = lawaid, public;

BEGIN;

-- deterministic UUID helper:  pg_temp.u('a0', 5) -> a0000000-0000-7000-8000-000000000005
CREATE FUNCTION pg_temp.u(p text, n int) RETURNS uuid LANGUAGE sql IMMUTABLE AS
$$ SELECT (p || '000000-0000-7000-8000-' || lpad(n::text, 12, '0'))::uuid $$;
-- prefixes: a0 users | b0 slots | c0 appointments | e0 cases | e1 hearings | e2 documents | f0 conversations | f1 ai conversations

-- ---------------------------------------------------------------------
-- Reference data
-- ---------------------------------------------------------------------
INSERT INTO courts (id, name, court_type, district) VALUES
 (1,  'Supreme Court of Bangladesh - High Court Division', 'supreme_court', 'Dhaka'),
 (2,  'Supreme Court of Bangladesh - Appellate Division',  'supreme_court', 'Dhaka'),
 (3,  'Dhaka District & Sessions Court',                   'district',      'Dhaka'),
 (4,  'Dhaka Metropolitan Sessions Court',                 'district',      'Dhaka'),
 (5,  'Family Court No. 2, Dhaka',                         'family',        'Dhaka'),
 (6,  'Administrative Tribunal, Dhaka',                    'tribunal',      'Dhaka'),
 (7,  'Artha Rin Adalat, Dhaka',                           'special',       'Dhaka'),
 (8,  'Chattogram District Court',                         'district',      'Chattogram'),
 (9,  'Labour Court, Dhaka',                               'tribunal',      'Dhaka'),
 (10, 'Cyber Tribunal, Dhaka',                             'tribunal',      'Dhaka');

INSERT INTO practice_areas (id, slug, name_en, name_bn) VALUES
 (1,  'constitutional',  'Constitutional / Writ',     'সাংবিধানিক / রিট'),
 (2,  'corporate',       'Corporate & Commercial',    'কর্পোরেট ও বাণিজ্যিক'),
 (3,  'criminal',        'Criminal Defense',          'ফৌজদারি প্রতিরক্ষা'),
 (4,  'civil-property',  'Civil & Property',          'দেওয়ানি ও সম্পত্তি'),
 (5,  'family',          'Family & Custody',          'পারিবারিক ও অভিভাবকত্ব'),
 (6,  'labor',           'Labor Law',                 'শ্রম আইন'),
 (7,  'cyber',           'Cyber Law',                 'সাইবার আইন'),
 (8,  'banking',         'Banking & Artha Rin',       'ব্যাংকিং ও অর্থঋণ'),
 (9,  'inheritance',     'Inheritance & Probate',     'উত্তরাধিকার ও প্রোবেট'),
 (10, 'anti-corruption', 'Anti-Corruption (ACC)',     'দুর্নীতি দমন'),
 (11, 'arbitration',     'Arbitration',               'সালিশ'),
 (12, 'ip',              'Intellectual Property',     'বুদ্ধিবৃত্তিক সম্পত্তি');

-- ---------------------------------------------------------------------
-- Users   (2 admins, 7 lawyers incl. 1 pending + 1 rejected, 10 clients)
-- ---------------------------------------------------------------------
INSERT INTO users (id, role, full_name, email, phone, password_hash, preferred_language, status, avatar_url, two_factor_enabled, email_verified_at, phone_verified_at) VALUES
 (pg_temp.u('a0', 1),  'admin',  'Rahid Karim',                   'rahid.karim@lawaid.com.bd',     '+8801711000001', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', NULL, true,  now(), now()),
 (pg_temp.u('a0', 2),  'admin',  'Nafseen Hossain',               'nafseen.hossain@lawaid.com.bd', '+8801711000002', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', NULL, true,  now(), now()),
 -- lawyers
 (pg_temp.u('a0', 11), 'lawyer', 'Rafiqul Islam',                 'rafiqul.islam@lawaid.com.bd',   '+8801712000011', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/lawyer-rafiqul-islam.jpg',   true,  now(), now()),
 (pg_temp.u('a0', 12), 'lawyer', 'Nusrat Adil',                   'nusrat.adil@lawaid.com.bd',     '+8801712000012', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/lawyer-nusrat-adil.jpg',       true,  now(), now()),
 (pg_temp.u('a0', 13), 'lawyer', 'Mukarram Hossain',              'mukarram.hossain@lawaid.com.bd','+8801712000013', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/lawyer-mukarram-hossain.jpg',  true,  now(), now()),
 (pg_temp.u('a0', 14), 'lawyer', 'Tariq Rahman',                  'tariq.rahman@lawaid.com.bd',    '+8801712000014', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', NULL,                                              true,  now(), now()),
 (pg_temp.u('a0', 15), 'lawyer', 'Rezwana Karim',                 'rezwana.karim@lawaid.com.bd',   '+8801712000015', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', NULL,                                              true,  now(), now()),
 (pg_temp.u('a0', 16), 'lawyer', 'Farhan Chowdhury',              'farhan.chowdhury@example.com',  '+8801712000016', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'pending_verification', NULL,                                 false, now(), now()),
 (pg_temp.u('a0', 17), 'lawyer', 'Imran Sheikh',                  'imran.sheikh@example.com',      '+8801712000017', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'pending_verification', NULL,                                 false, now(), now()),
 -- clients
 (pg_temp.u('a0', 21), 'client', 'Ahnaf Shahriar',                'ahnaf.shahriar@example.com',    '+8801713000021', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', '/assets/img/avatars/user-ahnaf-shahriar.jpg',     false, now(), now()),
 (pg_temp.u('a0', 22), 'client', 'Ayesha Rahman',                 'ayesha.rahman@example.com',     '+8801713000022', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/client-ayesha-rahman.jpg',    false, now(), now()),
 (pg_temp.u('a0', 23), 'client', 'Dr. Farhana Chowdhury',         'farhana.chowdhury@example.com', '+8801713000023', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', '/assets/img/avatars/client-farhana-chowdhury.jpg',false, now(), now()),
 (pg_temp.u('a0', 24), 'client', 'Syed Mashood Haque',            'mashood.haque@example.com',     '+8801713000024', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', '/assets/img/avatars/client-syed-mashood-haque.jpg',false, now(), now()),
 (pg_temp.u('a0', 25), 'client', 'Anisul Haque',                  'anisul.haque@example.com',      '+8801713000025', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', '/assets/img/avatars/client-anisul-haque.jpg',      false, now(), now()),
 (pg_temp.u('a0', 26), 'client', 'Rezwana Ahmed',                 'rezwana.ahmed@example.com',     '+8801713000026', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/client-rezwana-ahmed.jpg',     false, now(), now()),
 (pg_temp.u('a0', 27), 'client', 'Rafiq Ahmed',                   'rafiq.ahmed@example.com',       '+8801713000027', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', '/assets/img/avatars/client-rafiq-ahmed.jpg',       false, now(), now()),
 (pg_temp.u('a0', 28), 'client', 'Junaid Hassan',                 'junaid.hassan@example.com',     '+8801713000028', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', '/assets/img/avatars/client-junaid-hassan.jpg',     false, now(), now()),
 (pg_temp.u('a0', 29), 'client', 'Syeda Farhana Begum',           'farhana.begum@example.com',     '+8801713000029', crypt('LawAid@123', gen_salt('bf', 8)), 'bn', 'active', NULL,                                              false, now(), now()),
 (pg_temp.u('a0', 30), 'client', 'Kazi Tanvir Ahmed',             'tanvir.ahmed@example.com',      '+8801713000030', crypt('LawAid@123', gen_salt('bf', 8)), 'en', 'active', NULL,                                              false, now(), now());

INSERT INTO client_profiles (user_id, gender, date_of_birth, organization_name, division, district, address) VALUES
 (pg_temp.u('a0', 21), 'male',   '2001-03-14', NULL,                          'Dhaka',      'Dhaka',      'Dhanmondi, Dhaka'),
 (pg_temp.u('a0', 22), 'female', '1994-08-22', NULL,                          'Dhaka',      'Dhaka',      'Mirpur, Dhaka'),
 (pg_temp.u('a0', 23), 'female', '1979-11-02', NULL,                          'Dhaka',      'Dhaka',      'Gulshan, Dhaka'),
 (pg_temp.u('a0', 24), 'male',   '1985-05-30', 'Biman Logistics Int''l Ltd.', 'Dhaka',      'Dhaka',      'Uttara, Dhaka'),
 (pg_temp.u('a0', 25), 'male',   '1972-01-19', 'Metro Housing Ltd.',          'Dhaka',      'Dhaka',      'Banani, Dhaka'),
 (pg_temp.u('a0', 26), 'female', '1990-09-09', NULL,                          'Chattogram', 'Chattogram', 'Khulshi, Chattogram'),
 (pg_temp.u('a0', 27), 'male',   '1983-12-25', NULL,                          'Sylhet',     'Sylhet',     'Zindabazar, Sylhet'),
 (pg_temp.u('a0', 28), 'male',   '1998-04-04', NULL,                          'Dhaka',      'Gazipur',    'Tongi, Gazipur'),
 (pg_temp.u('a0', 29), 'female', '1988-06-17', NULL,                          'Dhaka',      'Dhaka',      'Mohammadpur, Dhaka'),
 (pg_temp.u('a0', 30), 'male',   '1981-02-11', 'Apex Pharma Ltd.',            'Dhaka',      'Dhaka',      'Tejgaon, Dhaka');

INSERT INTO lawyer_profiles
 (user_id, honorific, headline, bar_council_no, bar_association, primary_court_id, chamber_address, district, latitude, longitude,
  years_experience, bio, consultation_fee, session_minutes, formats, offers_free_session, sos_available,
  verification_status, verified_at, verified_by) VALUES
 (pg_temp.u('a0', 11), 'Barrister', 'Senior Advocate, Supreme Court', 'SC-7841', 'Supreme Court Bar Association', 1,
  'Room 402, Supreme Court Bar Annex, Ramna, Dhaka', 'Dhaka', 23.7331, 90.3972, 18,
  'Property, land and civil writ matters before the High Court Division.', 1500, 30, '{video,audio,chat,in_person}', false, true,
  'approved', now() - interval '200 days', pg_temp.u('a0', 1)),
 (pg_temp.u('a0', 12), 'Adv.', 'Advocate, Dhaka District & Sessions Court', 'DH-10492', 'Dhaka Bar Association', 3,
  'Judge Court Building, Dhaka', 'Dhaka', 23.7104, 90.4074, 11,
  'Family law, custody, inheritance and cyber-harassment matters.', 800, 30, '{video,audio,chat,in_person}', true, false,
  'approved', now() - interval '180 days', pg_temp.u('a0', 1)),
 (pg_temp.u('a0', 13), 'Adv.', 'Advocate, High Court Division', 'SC-9230', 'Supreme Court Bar Association', 1,
  'Purana Paltan, Dhaka', 'Dhaka', 23.7340, 90.4125, 14,
  'Criminal defense, ACC cases and labor disputes. Available for emergency calls.', 1000, 30, '{video,audio,chat}', false, true,
  'approved', now() - interval '170 days', pg_temp.u('a0', 1)),
 (pg_temp.u('a0', 14), 'Barrister', 'Advocate, Appellate Division', 'SC-4412', 'Supreme Court Bar Association', 2,
  'Motijheel Commercial Area, Dhaka', 'Dhaka', 23.7330, 90.4172, 22,
  'Banking, Artha Rin, company incorporation and arbitration panel member.', 2000, 45, '{video,audio,chat,in_person}', false, false,
  'approved', now() - interval '160 days', pg_temp.u('a0', 1)),
 (pg_temp.u('a0', 15), 'Adv.', 'Senior Advocate, SC', 'SC-5520', 'Supreme Court Bar Association', 1,
  'Supreme Court Bar Annex Building, Ramna, Dhaka 1000', 'Dhaka', 23.7316, 90.3965, 21,
  'Writ, land, corporate and family litigation; lead counsel on complex multi-party matters.', 2500, 60, '{video,audio,chat,in_person}', false, true,
  'approved', now() - interval '150 days', pg_temp.u('a0', 1)),
 (pg_temp.u('a0', 16), 'Adv.', 'Advocate', 'DH-22871', 'Dhaka Bar Association', 3,
  'Nayabazar, Dhaka', 'Dhaka', NULL, NULL, 4,
  NULL, 600, 30, '{video,audio,chat}', true, false, 'pending', NULL, NULL),
 (pg_temp.u('a0', 17), 'Adv.', 'Advocate', 'CTG-3310', 'Chattogram Bar Association', 8,
  'Andarkilla, Chattogram', 'Chattogram', NULL, NULL, 2,
  NULL, 500, 30, '{video,audio,chat}', false, false, 'rejected', NULL, pg_temp.u('a0', 2));

INSERT INTO lawyer_practice_areas (lawyer_id, practice_area_id) VALUES
 (pg_temp.u('a0', 11), 4), (pg_temp.u('a0', 11), 1), (pg_temp.u('a0', 11), 2),
 (pg_temp.u('a0', 12), 5), (pg_temp.u('a0', 12), 9), (pg_temp.u('a0', 12), 7),
 (pg_temp.u('a0', 13), 3), (pg_temp.u('a0', 13), 10), (pg_temp.u('a0', 13), 6),
 (pg_temp.u('a0', 14), 8), (pg_temp.u('a0', 14), 2), (pg_temp.u('a0', 14), 11),
 (pg_temp.u('a0', 15), 1), (pg_temp.u('a0', 15), 2), (pg_temp.u('a0', 15), 4), (pg_temp.u('a0', 15), 5), (pg_temp.u('a0', 15), 11), (pg_temp.u('a0', 15), 12),
 (pg_temp.u('a0', 16), 3), (pg_temp.u('a0', 17), 4);

INSERT INTO lawyer_verification_documents (lawyer_id, doc_type, file_url, status, rejection_reason, submitted_at, reviewed_by, reviewed_at)
SELECT lp.user_id, d.t, 'private://verification/' || lp.bar_council_no || '/' || d.t || '.pdf',
       CASE lp.verification_status WHEN 'approved' THEN 'approved'::verification_status
                                   WHEN 'rejected' THEN 'rejected'::verification_status
                                   ELSE 'pending'::verification_status END,
       CASE WHEN lp.verification_status = 'rejected' AND d.t = 'bar_certificate'
            THEN 'Certificate number does not match Bar Council of Bangladesh records.' END,
       now() - interval '210 days',
       CASE WHEN lp.verification_status <> 'pending' THEN lp.verified_by END,
       CASE WHEN lp.verification_status <> 'pending' THEN now() - interval '200 days' END
FROM lawyer_profiles lp CROSS JOIN (VALUES ('nid'::verification_doc), ('bar_certificate'::verification_doc)) d(t)
WHERE NOT (lp.verification_status = 'rejected' AND d.t = 'nid')
UNION ALL
SELECT lp.user_id, 'nid', 'private://verification/' || lp.bar_council_no || '/nid.pdf', 'approved', NULL,
       now() - interval '5 days', pg_temp.u('a0', 2), now() - interval '4 days'
FROM lawyer_profiles lp WHERE lp.verification_status = 'rejected';

-- ---------------------------------------------------------------------
-- Availability slots
-- ---------------------------------------------------------------------
-- explicit slots referenced by appointments
INSERT INTO lawyer_availability_slots (id, lawyer_id, starts_at, ends_at, formats) VALUES
 (pg_temp.u('b0', 1),  pg_temp.u('a0', 11), current_date::timestamptz + interval '1 day 16 hours 30 minutes', current_date::timestamptz + interval '1 day 17 hours',  '{video,audio,chat,in_person}'),
 (pg_temp.u('b0', 4),  pg_temp.u('a0', 15), current_date::timestamptz + interval '15 hours 30 minutes',       current_date::timestamptz + interval '16 hours 30 minutes', '{video,audio,chat,in_person}'),
 (pg_temp.u('b0', 5),  pg_temp.u('a0', 15), current_date::timestamptz + interval '2 days 12 hours',           current_date::timestamptz + interval '2 days 13 hours',  '{video,audio,chat,in_person}'),
 (pg_temp.u('b0', 8),  pg_temp.u('a0', 12), current_date::timestamptz + interval '4 days 12 hours',           current_date::timestamptz + interval '4 days 12 hours 30 minutes', '{video,audio,chat,in_person}'),
 (pg_temp.u('b0', 10), pg_temp.u('a0', 12), current_date::timestamptz + interval '3 days 12 hours',           current_date::timestamptz + interval '3 days 12 hours 30 minutes', '{video,audio,chat,in_person}');

-- open slots for the next 7 days at 10:00 and 15:00
INSERT INTO lawyer_availability_slots (lawyer_id, starts_at, ends_at, formats)
SELECT pg_temp.u('a0', l.n),
       current_date::timestamptz + make_interval(days => g.day) + h.t,
       current_date::timestamptz + make_interval(days => g.day) + h.t + make_interval(mins => l.mins),
       CASE WHEN l.n IN (11, 12, 14, 15) THEN '{video,audio,chat,in_person}'::consultation_format[] ELSE '{video,audio,chat}'::consultation_format[] END
FROM (VALUES (11, 30), (12, 30), (13, 30), (14, 45), (15, 60)) l(n, mins)
CROSS JOIN generate_series(1, 7) g(day)
CROSS JOIN (VALUES (interval '10 hours'), (interval '15 hours')) h(t);

-- ---------------------------------------------------------------------
-- Cases  (needed before appointments that link to them)
-- ---------------------------------------------------------------------
INSERT INTO cases (id, case_no, title, category, nature_tag, practice_area_id, court_id, bench, jurisdiction, lawyer_id, client_id,
                   opposing_party, narrative, status, urgency, filed_at, disposed_at, final_judgment, stamp_fee_bdt) VALUES
 (pg_temp.u('e0', 1), 'CP-2026-0491', 'Metro Housing Ltd. vs. Land Ministry & Ors.', 'Writ Petition', 'WRIT & LAND DISPUTE', 1, 1,
  'Hon. Justice M. A. Rahman (Bench 07)', 'High Court Division, Appellate & Original', pg_temp.u('a0', 15), pg_temp.u('a0', 25),
  'Ministry of Land',
  'Petitioner asserts freehold title over 4.8 acres of urban commercial land under Registry Deed #7821/18, wrongfully demarcated as gazette acquisition without statutory notice. Prayers: injunction against boundary demarcation, reassessment of the survey map, and revocation of the summary eviction directive.',
  'in_progress', 'regular', current_date - 120, NULL, NULL, 200),
 (pg_temp.u('e0', 2), 'CR-2026-0418', 'Apex Pharma Ltd. vs. Delta Formulations (Patent Infringement)', 'Civil Suit', 'IP & COMMERCIAL', 12, 1,
  'Appellate Tribunal - Special Bench', 'High Court Division', pg_temp.u('a0', 15), pg_temp.u('a0', 30),
  'Delta Formulations Ltd.',
  'Alleged infringement of a process patent for an oral anti-diabetic formulation. Expert testimony submission is due this week.',
  'in_progress', 'urgent', current_date - 90, NULL, NULL, 200),
 (pg_temp.u('e0', 3), 'AR-2026-1102', 'Biman Logistics vs. Pacific Shipping Corp. (Demurrage Claim)', 'Arbitration', 'MARITIME ARBITRATION', 11, 4,
  'Barrister Kamal Hossain, KC', 'Chamber A, Arbitration Centre', pg_temp.u('a0', 15), pg_temp.u('a0', 24),
  'Pacific Shipping Corp.',
  'Demurrage and detention claim arising from delayed container release at Chattogram port.',
  'pending_review', 'regular', current_date - 60, NULL, NULL, NULL),
 (pg_temp.u('e0', 4), 'FM-2025-4219', 'Hassan Estate - Probate & Distribution Decree', 'Succession Suit', 'FAMILY SUCCESSION', 9, 5,
  'Judge Shireen Akhtar (District 01)', 'Family Court No. 2, Dhaka', pg_temp.u('a0', 15), pg_temp.u('a0', 23),
  'Legal heirs (co-claimants)',
  'Probate and distribution of the Hassan estate among legal heirs. Final decree registered with Land Registry; escrow released.',
  'disposed', 'regular', current_date - 400, current_date - 30, 'Decree granted; certified copy issued.', 200),
 (pg_temp.u('e0', 5), 'CV-2026-0132', 'Shahriar vs. Gulshan Developers (Illegal Eviction & Mutation)', 'Civil Suit', 'CIVIL PROPERTY', 4, 3,
  'Joint District Judge, Dhaka', 'Dhaka District & Sessions Court', pg_temp.u('a0', 11), pg_temp.u('a0', 21),
  'Gulshan Developers Ltd.',
  'Client was served an unlawful eviction notice; mutation (khatian) in the owner''s name is being disputed. Temporary injunction under Order 39 sought.',
  'open', 'urgent', current_date - 14, NULL, NULL, 200),
 (pg_temp.u('e0', 6), 'FM-2026-0207', 'Rahman vs. Rahman (Dissolution of Marriage & Custody)', 'Family Suit', 'FAMILY LAW', 5, 5,
  'Family Court No. 2', 'Family Court No. 2, Dhaka', pg_temp.u('a0', 15), pg_temp.u('a0', 22),
  'Respondent spouse',
  'Dissolution of marriage with child custody and maintenance claims; mediation attempted once.',
  'in_progress', 'regular', current_date - 45, NULL, NULL, 200);

INSERT INTO case_hearings (id, case_id, hearing_at, bench, courtroom, cause_list_item, purpose, status, outcome) VALUES
 (pg_temp.u('e1', 1), pg_temp.u('e0', 1), now() - interval '20 days',     'Bench 07', 'Courtroom 7', 9,  'Preliminary hearing',                 'held', 'Rule nisi issued; counter-affidavit directed.'),
 (pg_temp.u('e1', 2), pg_temp.u('e0', 1), now() + interval '3 days 10 hours', 'Bench 07', 'Courtroom 7', 12, 'Hearing on Injunction Application', 'scheduled', NULL),
 (pg_temp.u('e1', 3), pg_temp.u('e0', 2), now() + interval '3 days 10 hours', 'Special Bench', 'Courtroom 3', 5, 'Expert testimony submission',     'scheduled', NULL),
 (pg_temp.u('e1', 4), pg_temp.u('e0', 3), now() + interval '5 days 14 hours', 'Chamber A',  'Arbitration Chamber A', NULL, 'Cross-examination',         'scheduled', NULL),
 (pg_temp.u('e1', 5), pg_temp.u('e0', 5), now() + interval '6 days 11 hours', 'Joint District Judge', 'Court Room 12', 21, 'Hearing on temporary injunction (Order 39)', 'scheduled', NULL),
 (pg_temp.u('e1', 6), pg_temp.u('e0', 6), now() + interval '9 days 11 hours', 'Family Court No. 2', 'Court Room 2', 4, 'Second mediation round',     'scheduled', NULL),
 (pg_temp.u('e1', 7), pg_temp.u('e0', 4), now() - interval '30 days',     'District 01', 'Court Room 1', 3, 'Final judgment',                       'held', 'Final decree issued.');

INSERT INTO case_team_members (case_id, user_id, team_role) VALUES
 (pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Lead Senior Counsel'),
 (pg_temp.u('e0', 1), pg_temp.u('a0', 25), 'Client / Authorized Person'),
 (pg_temp.u('e0', 2), pg_temp.u('a0', 15), 'Lead Senior Counsel'),
 (pg_temp.u('e0', 2), pg_temp.u('a0', 30), 'Client / Corporate Counsel'),
 (pg_temp.u('e0', 3), pg_temp.u('a0', 15), 'Lead Counsel'),
 (pg_temp.u('e0', 3), pg_temp.u('a0', 24), 'Client'),
 (pg_temp.u('e0', 5), pg_temp.u('a0', 11), 'Lead Counsel'),
 (pg_temp.u('e0', 5), pg_temp.u('a0', 21), 'Client'),
 (pg_temp.u('e0', 6), pg_temp.u('a0', 15), 'Lead Counsel'),
 (pg_temp.u('e0', 6), pg_temp.u('a0', 22), 'Client');

INSERT INTO case_updates (case_id, author_id, message, is_client_visible, created_at) VALUES
 (pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Primary counter-affidavit filed and verified by Registry.', true,  now() - interval '2 hours'),
 (pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Hearing on injunction application listed as Item 12.',      true,  now() - interval '1 day'),
 (pg_temp.u('e0', 2), pg_temp.u('a0', 15), 'Urgent: expert testimony submission required by Friday.',    true,  now() - interval '3 hours'),
 (pg_temp.u('e0', 3), pg_temp.u('a0', 15), 'Cross-examination docket uploaded.',                         true,  now() - interval '1 day'),
 (pg_temp.u('e0', 4), pg_temp.u('a0', 15), 'Final decree registered with Land Registry. Escrow released.', true, now() - interval '28 days'),
 (pg_temp.u('e0', 5), pg_temp.u('a0', 11), 'Case opened after video consultation; documents requested.',  true, now() - interval '13 days'),
 (pg_temp.u('e0', 5), pg_temp.u('a0', 11), 'Internal note: weak point is the 2019 mutation record.',      false, now() - interval '12 days'),
 (pg_temp.u('e0', 6), pg_temp.u('a0', 15), 'Mediation round 1 concluded without settlement.',             true, now() - interval '10 days');

INSERT INTO case_documents (id, case_id, uploaded_by, title, category, filed_by_party, file_url, mime_type, size_bytes, page_count, status, verified_by, verified_at, review_note, uploaded_at) VALUES
 (pg_temp.u('e2', 1), pg_temp.u('e0', 1), pg_temp.u('a0', 25), 'Plaint.pdf',                       'Plaint',            'Metro Housing Ltd.',         'private://cases/CP-2026-0491/plaint.pdf',        'application/pdf', 1887436, 28, 'verified',        pg_temp.u('a0', 15), now() - interval '100 days', NULL, now() - interval '100 days'),
 (pg_temp.u('e2', 2), pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Written Statement of Defence.pdf', 'Written Statement', 'Ministry of Land',           'private://cases/CP-2026-0491/ws.pdf',            'application/pdf', 2516582, 19, 'verified',        pg_temp.u('a0', 15), now() - interval '90 days',  NULL, now() - interval '90 days'),
 (pg_temp.u('e2', 3), pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Rejoinder.pdf',                   'Rejoinder',         'Metro Housing Ltd.',         'private://cases/CP-2026-0491/rejoinder.pdf',     'application/pdf', 1258291, 12, 'verified',        pg_temp.u('a0', 15), now() - interval '80 days',  NULL, now() - interval '80 days'),
 (pg_temp.u('e2', 4), pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Application for Interim Relief.pdf','Miscellaneous',    'Metro Housing Ltd.',         'private://cases/CP-2026-0491/interim.pdf',       'application/pdf', 943718,  8,  'pending_review',  NULL, NULL, NULL, now() - interval '3 days'),
 (pg_temp.u('e2', 5), pg_temp.u('e0', 1), pg_temp.u('a0', 15), 'Additional Affidavit.pdf',        'Affidavit',         'Metro Housing Ltd.',         'private://cases/CP-2026-0491/affidavit.pdf',     'application/pdf', 1153434, 7,  'pending_review',  NULL, NULL, NULL, now() - interval '1 day'),
 (pg_temp.u('e2', 6), pg_temp.u('e0', 1), pg_temp.u('a0', 25), 'Site_Survey_Cadastral_Map_2023.dwg','Exhibit',         'Metro Housing Ltd.',         'private://cases/CP-2026-0491/survey.dwg',        'image/vnd.dwg',   9331712, NULL,'verified',        pg_temp.u('a0', 15), now() - interval '70 days',  NULL, now() - interval '70 days'),
 (pg_temp.u('e2', 7), pg_temp.u('e0', 2), pg_temp.u('a0', 15), 'Counter-Affidavit Draft.pdf',     'Affidavit',         'Apex Pharma Ltd.',           'private://cases/CR-2026-0418/counter.pdf',       'application/pdf', 12582912, 22,'pending_review',  NULL, NULL, NULL, now() - interval '5 hours'),
 (pg_temp.u('e2', 8), pg_temp.u('e0', 5), pg_temp.u('a0', 21), 'Certified Land Mutation Deed & Khatian.pdf','Exhibit',  'Client',                     'private://cases/CV-2026-0132/khatian.pdf',       'application/pdf', 4194304, 14, 'verified',        pg_temp.u('a0', 11), now() - interval '10 days',  NULL, now() - interval '11 days'),
 (pg_temp.u('e2', 9), pg_temp.u('e0', 5), pg_temp.u('a0', 21), 'Eviction Notice.jpg',             'Exhibit',           'Gulshan Developers Ltd.',    'private://cases/CV-2026-0132/notice.jpg',        'image/jpeg',      824320,  1,  'action_required', pg_temp.u('a0', 11), now() - interval '9 days',   'Image is cropped; please upload the full notice.', now() - interval '11 days'),
 (pg_temp.u('e2', 10),pg_temp.u('e0', 6), pg_temp.u('a0', 22), 'Marriage Certificate (Nikahnama).pdf','Exhibit',       'Client',                     'private://cases/FM-2026-0207/nikahnama.pdf',     'application/pdf', 1048576, 3,  'verified',        pg_temp.u('a0', 15), now() - interval '40 days',  NULL, now() - interval '41 days');

INSERT INTO document_requests (id, requested_by, recipient_type, recipient_user_id, recipient_name, case_id, status, due_at) VALUES
 (pg_temp.u('e2', 101), pg_temp.u('a0', 11), 'client', pg_temp.u('a0', 21), 'Ahnaf Shahriar', pg_temp.u('e0', 5), 'sent', now() + interval '5 days');
INSERT INTO document_request_items (request_id, label, priority) VALUES
 (pg_temp.u('e2', 101), 'Certified Land Mutation Deed & Khatian', 'URGENT'),
 (pg_temp.u('e2', 101), 'Power of Attorney / Vakalatnama',        'STANDARD'),
 (pg_temp.u('e2', 101), 'Full copy of the eviction notice',       'MANDATORY');

INSERT INTO tasks (lawyer_id, assignee_id, case_id, title, priority, status, due_at) VALUES
 (pg_temp.u('a0', 15), pg_temp.u('a0', 15), pg_temp.u('e0', 2), 'Draft Counter-Affidavit (Apex Pharma)',          'urgent', 'open', now() + interval '6 hours'),
 (pg_temp.u('a0', 15), pg_temp.u('a0', 15), pg_temp.u('e0', 3), 'RJSC Memorandum & Articles inspection',           'medium', 'open', now() + interval '1 day'),
 (pg_temp.u('a0', 15), pg_temp.u('a0', 15), pg_temp.u('e0', 6), 'Vakalatnama & Power of Attorney signatures',     'normal', 'open', now() + interval '3 days'),
 (pg_temp.u('a0', 15), pg_temp.u('a0', 15), pg_temp.u('e0', 1), 'Issue legal notice to Gulshan Developers',       'normal', 'open', now() + interval '5 days'),
 (pg_temp.u('a0', 15), pg_temp.u('a0', 15), pg_temp.u('e0', 4), 'Collect certified copy of final decree',         'normal', 'done', now() - interval '28 days'),
 (pg_temp.u('a0', 11), pg_temp.u('a0', 11), pg_temp.u('e0', 5), 'Prepare Order 39 injunction application',        'urgent', 'open', now() + interval '2 days');

INSERT INTO calendar_events (lawyer_id, event_type, title, location, case_id, hearing_id, starts_at, ends_at) VALUES
 (pg_temp.u('a0', 15), 'court_hearing',   'Hearing - CP-2026-0491 (Injunction Application)', 'HCD Bench 07',  pg_temp.u('e0', 1), pg_temp.u('e1', 2), now() + interval '3 days 10 hours',            now() + interval '3 days 11 hours 30 minutes'),
 (pg_temp.u('a0', 15), 'court_hearing',   'Hearing - CR-2026-0418 (Expert testimony)',       'Special Bench', pg_temp.u('e0', 2), pg_temp.u('e1', 3), now() + interval '3 days 10 hours',            now() + interval '3 days 11 hours'),
 (pg_temp.u('a0', 15), 'chamber_review',  'Chamber consultation - Ayesha Rahman',            'Room 402',      NULL, NULL,                          current_date::timestamptz + interval '15 hours 30 minutes', current_date::timestamptz + interval '16 hours 30 minutes'),
 (pg_temp.u('a0', 15), 'virtual_review',  'Virtual legal review - Apex Pharma',              'Video',         pg_temp.u('e0', 2), NULL,            now() + interval '2 days 14 hours 30 minutes',       now() + interval '2 days 15 hours 15 minutes'),
 (pg_temp.u('a0', 15), 'filing_deadline', 'Counter-affidavit submission deadline',           'Registry',      pg_temp.u('e0', 1), NULL,            now() + interval '10 days 16 hours',                 NULL);

-- ---------------------------------------------------------------------
-- Appointments  (covers every branch of the state diagram)
-- ---------------------------------------------------------------------
INSERT INTO appointments
 (id, client_id, lawyer_id, slot_id, case_id, practice_area_id, format, status, scheduled_start, scheduled_end,
  issue_summary, fee_amount, is_sos, ai_recommended, hold_expires_at, cancelled_by, cancel_reason) VALUES
 -- A01 confirmed (tomorrow, video, ai matched)
 (pg_temp.u('c0', 1),  pg_temp.u('a0', 21), pg_temp.u('a0', 11), pg_temp.u('b0', 1), pg_temp.u('e0', 5), 4, 'video', 'confirmed',
  current_date::timestamptz + interval '1 day 16 hours 30 minutes', current_date::timestamptz + interval '1 day 17 hours',
  'Illegal eviction notice from developer; need injunction advice.', 1500, false, true, NULL, NULL, NULL),
 -- A02 completed, awaiting client confirmation (escrow still held)
 (pg_temp.u('c0', 2),  pg_temp.u('a0', 21), pg_temp.u('a0', 12), NULL, NULL, 9, 'video', 'completed',
  now() - interval '3 days', now() - interval '3 days' + interval '30 minutes',
  'Inheritance share of ancestral property.', 800, false, false, NULL, NULL, NULL),
 -- A03 reviewed
 (pg_temp.u('c0', 3),  pg_temp.u('a0', 21), pg_temp.u('a0', 13), NULL, NULL, 6, 'audio', 'reviewed',
  now() - interval '10 days', now() - interval '10 days' + interval '30 minutes',
  'Unpaid overtime and wrongful termination.', 1000, false, true, NULL, NULL, NULL),
 -- A04 confirmed today
 (pg_temp.u('c0', 4),  pg_temp.u('a0', 22), pg_temp.u('a0', 15), pg_temp.u('b0', 4), pg_temp.u('e0', 6), 5, 'in_person', 'confirmed',
  current_date::timestamptz + interval '15 hours 30 minutes', current_date::timestamptz + interval '16 hours 30 minutes',
  'Divorce filing, child custody and alimony discussion.', 2500, false, false, NULL, NULL, NULL),
 -- A05 awaiting lawyer
 (pg_temp.u('c0', 5),  pg_temp.u('a0', 23), pg_temp.u('a0', 15), pg_temp.u('b0', 5), NULL, 9, 'video', 'awaiting_lawyer',
  current_date::timestamptz + interval '2 days 12 hours', current_date::timestamptz + interval '2 days 13 hours',
  'Second consultation on estate documentation.', 2500, false, true, NULL, NULL, NULL),
 -- A06 declined by lawyer -> escrow refunded
 (pg_temp.u('c0', 6),  pg_temp.u('a0', 24), pg_temp.u('a0', 14), NULL, NULL, 8, 'video', 'declined',
  now() - interval '6 days', now() - interval '6 days' + interval '45 minutes',
  'Artha Rin loan restructuring.', 2000, false, false, NULL, pg_temp.u('a0', 14), 'Conflict of interest.'),
 -- A07 reviewed
 (pg_temp.u('c0', 7),  pg_temp.u('a0', 25), pg_temp.u('a0', 15), NULL, pg_temp.u('e0', 1), 1, 'video', 'reviewed',
  now() - interval '20 days', now() - interval '20 days' + interval '1 hour',
  'Writ petition strategy for land acquisition.', 2500, false, true, NULL, NULL, NULL),
 -- A08 payment pending (slot on hold)
 (pg_temp.u('c0', 8),  pg_temp.u('a0', 26), pg_temp.u('a0', 12), pg_temp.u('b0', 8), NULL, 7, 'chat', 'payment_pending',
  current_date::timestamptz + interval '4 days 12 hours', current_date::timestamptz + interval '4 days 12 hours 30 minutes',
  'Online harassment and defamation.', 800, false, true, now() + interval '10 minutes', NULL, NULL),
 -- A09 disputed
 (pg_temp.u('c0', 9),  pg_temp.u('a0', 27), pg_temp.u('a0', 13), NULL, NULL, 3, 'audio', 'disputed',
  now() - interval '5 days', now() - interval '5 days' + interval '30 minutes',
  'Bail matter; client says the session ended after 8 minutes.', 1000, false, false, NULL, NULL, NULL),
 -- A10 free session confirmed (chat)
 (pg_temp.u('c0', 10), pg_temp.u('a0', 28), pg_temp.u('a0', 12), pg_temp.u('b0', 10), NULL, 5, 'chat', 'confirmed',
  current_date::timestamptz + interval '3 days 12 hours', current_date::timestamptz + interval '3 days 12 hours 30 minutes',
  'First-time free consultation about tenancy.', 0, false, false, NULL, NULL, NULL),
 -- A11 SOS (no slot)
 (pg_temp.u('c0', 11), pg_temp.u('a0', 29), pg_temp.u('a0', 13), NULL, NULL, 3, 'audio', 'confirmed',
  now() + interval '30 minutes', now() + interval '60 minutes',
  'EMERGENCY: family member detained overnight.', 1000, true, false, NULL, NULL, NULL),
 -- A12-A15 older reviewed sessions
 (pg_temp.u('c0', 12), pg_temp.u('a0', 30), pg_temp.u('a0', 11), NULL, NULL, 4, 'video', 'reviewed',
  now() - interval '30 days', now() - interval '30 days' + interval '30 minutes', 'Sale deed verification.', 1500, false, false, NULL, NULL, NULL),
 (pg_temp.u('c0', 13), pg_temp.u('a0', 22), pg_temp.u('a0', 11), NULL, NULL, 4, 'chat',  'reviewed',
  now() - interval '45 days', now() - interval '45 days' + interval '30 minutes', 'Rent agreement clause review.', 1500, false, false, NULL, NULL, NULL),
 (pg_temp.u('c0', 14), pg_temp.u('a0', 26), pg_temp.u('a0', 14), NULL, NULL, 2, 'video', 'reviewed',
  now() - interval '15 days', now() - interval '15 days' + interval '45 minutes', 'Company incorporation requirements.', 2000, false, true, NULL, NULL, NULL),
 (pg_temp.u('c0', 15), pg_temp.u('a0', 23), pg_temp.u('a0', 12), NULL, NULL, 5, 'audio', 'reviewed',
  now() - interval '25 days', now() - interval '25 days' + interval '30 minutes', 'Custody arrangement advice.', 800, false, false, NULL, NULL, NULL);

-- extra, realistic status history for the lifecycle of one booking (A02)
INSERT INTO appointment_status_history (appointment_id, from_status, to_status, changed_by, changed_at) VALUES
 (pg_temp.u('c0', 2), 'slot_reserved',   'payment_pending', pg_temp.u('a0', 21), now() - interval '4 days 2 hours'),
 (pg_temp.u('c0', 2), 'payment_pending', 'awaiting_lawyer', NULL,                now() - interval '4 days 1 hour 58 minutes'),
 (pg_temp.u('c0', 2), 'awaiting_lawyer', 'confirmed',       pg_temp.u('a0', 12), now() - interval '4 days 1 hour'),
 (pg_temp.u('c0', 2), 'confirmed',       'in_progress',     NULL,                now() - interval '3 days'),
 (pg_temp.u('c0', 2), 'in_progress',     'completed',       NULL,                now() - interval '3 days' + interval '31 minutes');

-- ---------------------------------------------------------------------
-- Payments / receipts / disputes / reviews / sessions
-- ---------------------------------------------------------------------
INSERT INTO payments (appointment_id, client_id, lawyer_id, amount, platform_fee, method, gateway_txn_id, status, escrow, paid_at, escrow_released_at, refunded_at)
SELECT a.id, a.client_id, a.lawyer_id, a.fee_amount, round(a.fee_amount * 0.10, 2), v.method::payment_method, v.txn,
       v.st::payment_status, v.esc::escrow_status,
       CASE WHEN v.st IN ('succeeded','refunded') THEN a.created_at - interval '1 hour' + v.paid_off END,
       CASE WHEN v.esc = 'released' THEN a.scheduled_end + interval '2 hours' END,
       CASE WHEN v.st = 'refunded' THEN a.scheduled_start + interval '1 hour' END
FROM appointments a
JOIN (VALUES
  (1,  'bkash',      'BK7H2K9A31', 'succeeded', 'held',     interval '0'),
  (2,  'bkash',      'BK3D8L2Q55', 'succeeded', 'held',     interval '0'),
  (3,  'nagad',      'NG5521098',  'succeeded', 'released', interval '0'),
  (4,  'sslcommerz', 'SSL-20-88412','succeeded','held',     interval '0'),
  (5,  'nagad',      'NG5521877',  'succeeded', 'held',     interval '0'),
  (6,  'bkash',      'BK1A1A0042', 'refunded',  'refunded', interval '0'),
  (7,  'sslcommerz', 'SSL-19-77310','succeeded','released', interval '0'),
  (8,  'bkash',      NULL,         'initiated', 'none',     interval '0'),
  (9,  'bkash',      'BK9Z0Q7712', 'succeeded', 'disputed', interval '0'),
  (11, 'nagad',      'NG5522001',  'succeeded', 'held',     interval '0'),
  (12, 'bkash',      'BK4412FF01', 'succeeded', 'released', interval '0'),
  (13, 'sslcommerz', 'SSL-12-10551','succeeded','released', interval '0'),
  (14, 'nagad',      'NG5519940',  'succeeded', 'released', interval '0'),
  (15, 'bkash',      'BK2200AB19', 'succeeded', 'released', interval '0')
) v(n, method, txn, st, esc, paid_off) ON a.id = pg_temp.u('c0', v.n);

INSERT INTO receipts (payment_id)
SELECT id FROM payments WHERE status IN ('succeeded', 'refunded');

INSERT INTO payment_disputes (payment_id, raised_by, reason, status)
SELECT p.id, p.client_id, 'Session ended after about 8 minutes of a 30-minute booking.', 'open'
FROM payments p WHERE p.appointment_id = pg_temp.u('c0', 9);

INSERT INTO reviews (appointment_id, client_id, lawyer_id, rating, comment, created_at)
SELECT a.id, a.client_id, a.lawyer_id, v.rating, v.comment, a.scheduled_end + interval '1 day'
FROM appointments a
JOIN (VALUES
  (3,  5, 'Clear, practical advice on my labor dispute.'),
  (7,  5, 'Excellent grasp of writ jurisdiction; very responsive.'),
  (12, 4, 'Thorough document review. Call started a few minutes late.'),
  (13, 5, 'Explained every clause in plain Bangla.'),
  (14, 5, 'Saved us weeks on the incorporation process.'),
  (15, 5, 'Compassionate and professional.')
) v(n, rating, comment) ON a.id = pg_temp.u('c0', v.n);

INSERT INTO consultation_sessions (appointment_id, started_at, ended_at)
SELECT a.id, a.scheduled_start, CASE WHEN a.id = pg_temp.u('c0', 9) THEN a.scheduled_start + interval '8 minutes' ELSE a.scheduled_end END
FROM appointments a WHERE a.status IN ('completed', 'reviewed', 'disputed');

INSERT INTO sos_requests (id, client_id, description, latitude, longitude, status, lawyer_id, appointment_id, requested_at, accepted_at) VALUES
 (pg_temp.u('c0', 901), pg_temp.u('a0', 29), 'Family member detained at police station overnight; need immediate advice.', 23.7640, 90.3589,
  'accepted', pg_temp.u('a0', 13), pg_temp.u('c0', 11), now() - interval '4 minutes', now() - interval '2 minutes');

-- relationship table derived from real work
INSERT INTO lawyer_clients (lawyer_id, client_id, since)
SELECT lawyer_id, client_id, min(d)::date FROM (
  SELECT lawyer_id, client_id, created_at AS d FROM appointments
  UNION ALL SELECT lawyer_id, client_id, created_at FROM cases
) x GROUP BY lawyer_id, client_id;

-- ---------------------------------------------------------------------
-- Messaging
-- ---------------------------------------------------------------------
INSERT INTO conversations (id, client_id, lawyer_id, case_id) VALUES
 (pg_temp.u('f0', 1), pg_temp.u('a0', 22), pg_temp.u('a0', 15), pg_temp.u('e0', 6)),
 (pg_temp.u('f0', 2), pg_temp.u('a0', 21), pg_temp.u('a0', 11), pg_temp.u('e0', 5));

INSERT INTO messages (conversation_id, sender_id, msg_type, body, attachment_url, attachment_name, sent_at, read_at) VALUES
 (pg_temp.u('f0', 1), pg_temp.u('a0', 15), 'text', 'Good afternoon. I have received the case documents you submitted for FM-2026-0207.', NULL, NULL, now() - interval '3 hours', now() - interval '3 hours' + interval '5 minutes'),
 (pg_temp.u('f0', 1), pg_temp.u('a0', 22), 'text', 'Thank you. I wanted to confirm everything is in order before Thursday.',                NULL, NULL, now() - interval '2 hours 50 minutes', now() - interval '2 hours 45 minutes'),
 (pg_temp.u('f0', 1), pg_temp.u('a0', 15), 'text', 'The documents look strong, we can proceed. Please bring the original power of attorney when we meet.', NULL, NULL, now() - interval '2 hours 30 minutes', now() - interval '2 hours 20 minutes'),
 (pg_temp.u('f0', 1), pg_temp.u('a0', 15), 'text', 'Also prepare the title deed copy from the registry, if available.',                     NULL, NULL, now() - interval '2 hours 29 minutes', NULL),
 (pg_temp.u('f0', 2), pg_temp.u('a0', 21), 'file', NULL, 'private://chat/eviction-notice-full.pdf', 'eviction-notice-full.pdf', now() - interval '1 day', now() - interval '23 hours'),
 (pg_temp.u('f0', 2), pg_temp.u('a0', 11), 'text', 'Received. I will draft the Order 39 application and share it for your review tomorrow.', NULL, NULL, now() - interval '22 hours', NULL);

-- ---------------------------------------------------------------------
-- AI assistant + AI matching
-- ---------------------------------------------------------------------
INSERT INTO ai_conversations (id, user_id, session_token, language, title, module) VALUES
 (pg_temp.u('f1', 1), pg_temp.u('a0', 21), NULL,              'bn', 'Civil Property Dispute: Illegal Eviction', 'Civil & Property'),
 (pg_temp.u('f1', 2), NULL,                'anon-7f3c91b2',   'en', 'What are my rights if arrested?',          'General Legal Questions');

INSERT INTO ai_messages (conversation_id, role, content, language, model, prompt_tokens, completion_tokens, is_out_of_scope, disclaimer_shown, citations, flagged_for_review, created_at) VALUES
 (pg_temp.u('f1', 1), 'user',      'আমার বাড়িওয়ালা কোনো নোটিশ ছাড়াই আমাকে উচ্ছেদ করতে চাইছে। আমি কী করতে পারি?', 'bn', NULL, NULL, NULL, false, false, NULL, false, now() - interval '2 days'),
 (pg_temp.u('f1', 1), 'assistant', 'সাধারণভাবে, বৈধ নোটিশ ছাড়া উচ্ছেদ আইনসম্মত নয়। আপনি দেওয়ানি আদালতে অস্থায়ী নিষেধাজ্ঞার (Order 39) আবেদন করতে পারেন। এটি সাধারণ তথ্য; আপনার নির্দিষ্ট ক্ষেত্রে পরামর্শের জন্য একজন যাচাইকৃত আইনজীবীর সাথে কথা বলুন।', 'bn', 'gemini-2.5-flash', 412, 168, false, true, NULL, false, now() - interval '2 days' + interval '4 seconds'),
 (pg_temp.u('f1', 2), 'user',      'What are my basic rights if I am arrested by the police?', 'en', NULL, NULL, NULL, false, false, NULL, false, now() - interval '1 day'),
 (pg_temp.u('f1', 2), 'assistant', 'In general, an arrested person has the right to be informed of the grounds of arrest, to consult a lawyer of their choice, and to be produced before a magistrate within 24 hours. This is general information, not legal advice.', 'en', 'gemini-2.5-flash', 380, 120, false, true, '[{"act":"Constitution of Bangladesh","section":"Article 33"}]', false, now() - interval '1 day' + interval '3 seconds'),
 (pg_temp.u('f1', 2), 'user',      'Should I plead guilty in my pending case? Here are the facts...', 'en', NULL, NULL, NULL, false, false, NULL, false, now() - interval '1 day' + interval '2 minutes'),
 (pg_temp.u('f1', 2), 'assistant', 'I cannot give case-specific legal advice. Please book a verified criminal-defense lawyer on LawAid for guidance on your situation.', 'en', 'gemini-2.5-flash', 300, 60, true, true, NULL, true, now() - interval '1 day' + interval '2 minutes 3 seconds');

WITH rec AS (
  INSERT INTO ai_recommendations (client_id, issue_text, filters)
  VALUES (pg_temp.u('a0', 21), 'Landlord/developer is evicting me without notice and disputing my property mutation.',
          '{"district":"Dhaka","max_fee":2500,"min_rating":4.5}') RETURNING id)
INSERT INTO ai_recommendation_items (recommendation_id, lawyer_id, rank, score, reason)
SELECT rec.id, v.lawyer, v.rank, v.score, v.reason FROM rec, (VALUES
  (pg_temp.u('a0', 11), 1::smallint, 0.9420, 'Specialises in civil property and writ matters; 18 years; next slot tomorrow.'),
  (pg_temp.u('a0', 15), 2::smallint, 0.8810, 'Property and land litigation; higher fee than your filter midpoint.'),
  (pg_temp.u('a0', 12), 3::smallint, 0.6120, 'Inheritance and family property experience; lower fee.')
) v(lawyer, rank, score, reason);

-- ---------------------------------------------------------------------
-- Reports, notifications, audit, CMS, settings
-- ---------------------------------------------------------------------
INSERT INTO confidential_reports (reporter_id, is_anonymous, lawyer_id, lawyer_name_text, appointment_id, violation_type, statement, status, admin_notes, handled_by) VALUES
 (NULL,                true,  pg_temp.u('a0', 13), 'Adv. Mukarram Hossain', NULL, 'Chamber Overcharging / Escrow Bypass',
  'I was asked to pay an extra amount in cash outside the platform for the same session.', 'submitted', NULL, NULL),
 (pg_temp.u('a0', 27), false, pg_temp.u('a0', 13), 'Adv. Mukarram Hossain', pg_temp.u('c0', 9), 'Service Not Delivered',
  'Session ended after eight minutes without explanation.', 'under_review', 'Cross-checking session log against dispute.', pg_temp.u('a0', 2));

INSERT INTO data_deletion_requests (user_id, status, reason) VALUES
 (pg_temp.u('a0', 28), 'requested', 'No longer using the service.');

INSERT INTO notifications (user_id, channel, kind, title, body, entity_type, entity_id, status, scheduled_for, sent_at, read_at) VALUES
 (pg_temp.u('a0', 21), 'push', 'appointment_reminder', 'Consultation tomorrow at 4:30 PM', 'Video session with Barrister Rafiqul Islam, SC.', 'appointment', pg_temp.u('c0', 1), 'sent', now() - interval '1 hour', now() - interval '1 hour', NULL),
 (pg_temp.u('a0', 21), 'sms',  'appointment_reminder', 'LawAid: consultation tomorrow 4:30 PM with Adv. Rafiqul Islam.', NULL, 'appointment', pg_temp.u('c0', 1), 'sent', now() - interval '1 hour', now() - interval '1 hour', NULL),
 (pg_temp.u('a0', 21), 'in_app','payment_due',         'Please confirm session completion', 'Confirm your session with Adv. Nusrat Adil to release escrow.', 'appointment', pg_temp.u('c0', 2), 'sent', now() - interval '2 days', now() - interval '2 days', NULL),
 (pg_temp.u('a0', 15), 'push', 'booking_request',     'New booking request', 'Dr. Farhana Chowdhury requested a video consultation.', 'appointment', pg_temp.u('c0', 5), 'sent', now() - interval '3 hours', now() - interval '3 hours', NULL),
 (pg_temp.u('a0', 15), 'sms',  'hearing_reminder',    'Hearing in 3 days', 'CP-2026-0491 Injunction Application, Bench 07, 10:00 AM.', 'hearing', pg_temp.u('e1', 2), 'queued', now() + interval '2 days 10 hours', NULL, NULL),
 (pg_temp.u('a0', 13), 'push', 'sos_alert',           'SOS request nearby', 'A client needs urgent help. Accept within 5 minutes.', 'sos_request', pg_temp.u('c0', 901), 'sent', now() - interval '4 minutes', now() - interval '4 minutes', now() - interval '3 minutes'),
 (pg_temp.u('a0', 16), 'email','verification',        'Verification under review', 'Your NID and Bar Council certificate are being reviewed.', NULL, NULL, 'sent', now() - interval '1 day', now() - interval '1 day', NULL),
 (pg_temp.u('a0', 1),  'in_app','verification',       'Lawyer awaiting verification', 'Farhan Chowdhury submitted documents.', 'lawyer', pg_temp.u('a0', 16), 'sent', now() - interval '1 day', now() - interval '1 day', NULL);

INSERT INTO audit_logs (actor_id, actor_role, action, entity_type, entity_id, ip_address, metadata, created_at) VALUES
 (pg_temp.u('a0', 21), 'client', 'booking.create',     'appointment', pg_temp.u('c0', 1)::text,  '103.145.10.21', '{"format":"video","fee":1500}', now() - interval '1 day'),
 (pg_temp.u('a0', 21), 'client', 'payment.succeeded',  'appointment', pg_temp.u('c0', 1)::text,  '103.145.10.21', '{"method":"bkash","amount":1500}', now() - interval '1 day'),
 (pg_temp.u('a0', 11), 'lawyer', 'booking.accept',     'appointment', pg_temp.u('c0', 1)::text,  '103.145.22.8',  '{}', now() - interval '23 hours'),
 (pg_temp.u('a0', 15), 'lawyer', 'document.upload',    'case_document', pg_temp.u('e2', 7)::text, '103.145.22.9', '{"case":"CR-2026-0418"}', now() - interval '5 hours'),
 (pg_temp.u('a0', 1),  'admin',  'lawyer.verify',      'lawyer_profile', pg_temp.u('a0', 11)::text, '10.0.0.5', '{"decision":"approved"}', now() - interval '200 days'),
 (pg_temp.u('a0', 2),  'admin',  'lawyer.reject',      'lawyer_profile', pg_temp.u('a0', 17)::text, '10.0.0.6', '{"decision":"rejected","reason":"certificate mismatch"}', now() - interval '4 days'),
 (pg_temp.u('a0', 27), 'client', 'payment.dispute',    'payment',     pg_temp.u('c0', 9)::text,  '103.145.30.4', '{}', now() - interval '4 days');

INSERT INTO content_items (slug, kind, title_en, title_bn, body_en, body_bn, is_published, author_id) VALUES
 ('rights-on-arrest',  'legal_guide', 'Your Basic Rights on Arrest', 'গ্রেপ্তারের সময় আপনার মৌলিক অধিকার',
  'You must be told the grounds of arrest, may consult a lawyer, and must be produced before a magistrate within 24 hours.',
  'গ্রেপ্তারের কারণ জানার, আইনজীবীর সাথে পরামর্শ করার এবং ২৪ ঘণ্টার মধ্যে ম্যাজিস্ট্রেটের সামনে হাজির হওয়ার অধিকার আপনার আছে।', true, pg_temp.u('a0', 2)),
 ('ai-disclaimer',     'policy',      'AI Assistant Disclaimer', 'এআই সহকারীর দাবিত্যাগ',
  'LawAid AI provides general legal information only and is not a substitute for advice from a verified lawyer.',
  'LawAid এআই শুধু সাধারণ আইনি তথ্য দেয়; এটি যাচাইকৃত আইনজীবীর পরামর্শের বিকল্প নয়।', true, pg_temp.u('a0', 1)),
 ('how-escrow-works',  'faq',         'How does escrow payment work?', 'এসক্রো পেমেন্ট কীভাবে কাজ করে?',
  'Your fee is held securely and released to the lawyer only after the consultation is confirmed complete.',
  'আপনার ফি নিরাপদে রাখা হয় এবং পরামর্শ সম্পন্ন নিশ্চিত হলে আইনজীবীকে দেওয়া হয়।', true, pg_temp.u('a0', 2));

INSERT INTO system_settings (key, value, description, updated_by) VALUES
 ('platform_fee_percent',     '10',                               'Commission taken from each paid consultation', pg_temp.u('a0', 1)),
 ('slot_hold_minutes',        '15',                               'Minutes a slot is held while payment is pending', pg_temp.u('a0', 1)),
 ('sos_response_timeout_sec', '300',                              'Seconds before an SOS request is re-routed',    pg_temp.u('a0', 1)),
 ('supported_languages',      '["bn","en"]',                      'UI and chatbot languages',                      pg_temp.u('a0', 1)),
 ('ai_model',                 '"gemini-2.5-flash"',               'Default LLM used by the legal assistant',       pg_temp.u('a0', 1));

-- ---------------------------------------------------------------------
-- housekeeping: align identity sequences with explicit ids
-- ---------------------------------------------------------------------
SELECT setval(pg_get_serial_sequence('lawaid.courts', 'id'),          (SELECT max(id) FROM lawaid.courts));
SELECT setval(pg_get_serial_sequence('lawaid.practice_areas', 'id'),  (SELECT max(id) FROM lawaid.practice_areas));

COMMIT;

-- quick check
-- SELECT * FROM lawaid.v_admin_overview;
-- SELECT full_name, avg_rating, review_count, next_slot FROM lawaid.v_lawyer_search ORDER BY avg_rating DESC;
