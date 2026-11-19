import os
import io
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from accounts.models import User, LawyerProfile, LawyerVerificationDocument, VerificationStatus, UserRole
from accounts.encryption import DocumentEncryptionService

class Command(BaseCommand):
    help = 'Seeds initial demo users, lawyers with encrypted documents, and verification states for LawAid.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding LawAid demo data...")

        # 1. Create Lead Platform Admin (Rahid Karim)
        admin, created = User.objects.get_or_create(
            email='admin@lawaid.gov.bd',
            defaults={
                'full_name': 'Rahid Karim (Lead Administrator)',
                'role': UserRole.ADMIN,
                'phone': '+8801700000001',
                'is_staff': True,
                'is_superuser': True,
                'status': 'active'
            }
        )
        if created:
            admin.set_password('LawAid@123')
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created Admin: admin@lawaid.gov.bd (Password: LawAid@123)"))

        # 2. Create Regular Client (Ahnaf Shahriar)
        client, created = User.objects.get_or_create(
            email='ahnaf@gmail.com',
            defaults={
                'full_name': 'Ahnaf Shahriar',
                'role': UserRole.CLIENT,
                'phone': '+8801700000002',
                'status': 'active'
            }
        )
        if created:
            client.set_password('LawAid@123')
            client.save()
            self.stdout.write(self.style.SUCCESS("Created Client: ahnaf@gmail.com (Password: LawAid@123)"))

        # Helper to create a lawyer with encrypted verification documents
        def create_lawyer_with_docs(name, email, phone, honorific, headline, bar_no, bar_assoc, district, spec, fee, exp, status, rejection_reason=None):
            user, u_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'role': UserRole.LAWYER,
                    'phone': phone,
                    'status': 'active'
                }
            )
            if u_created:
                user.set_password('LawAid@123')
                user.save()

            verified_at = timezone.now() if status == VerificationStatus.APPROVED else None
            verified_by = admin if status == VerificationStatus.APPROVED else None

            profile, p_created = LawyerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'honorific': honorific,
                    'headline': headline,
                    'bar_council_no': bar_no,
                    'bar_association': bar_assoc,
                    'district': district,
                    'specialization': spec,
                    'consultation_fee': fee,
                    'years_experience': exp,
                    'verification_status': status,
                    'verified_at': verified_at,
                    'verified_by': verified_by,
                    'rejection_reason': rejection_reason,
                    'avg_rating': 4.90 if status == VerificationStatus.APPROVED else 0.0,
                    'review_count': 15 if status == VerificationStatus.APPROVED else 0,
                    'bio': f"{exp}+ years practicing advocate specializing in {spec} at {bar_assoc}."
                }
            )

            # Generate and encrypt dummy NID and Bar Council documents
            if not profile.verification_documents.exists():
                nid_bytes = f"BANGLADESH NATIONAL ID CARD\nNID No: {1980000000000000 + int(phone[-8:])}\nHolder: {name}".encode('utf-8')
                bar_bytes = f"BANGLADESH BAR COUNCIL SANAD CERTIFICATE\nSanad ID: {bar_no}\nBar Association: {bar_assoc}\nAdvocate: {name}".encode('utf-8')

                nid_saved = DocumentEncryptionService.save_encrypted_file(
                    SimpleUploadedFile(f"{bar_no}_NID.pdf", nid_bytes, "application/pdf"),
                    lawyer_id=str(user.id),
                    doc_type="nid"
                )
                LawyerVerificationDocument.objects.create(
                    lawyer=profile,
                    doc_type='nid',
                    file_path=nid_saved['file_path'],
                    original_filename=nid_saved['original_filename'],
                    mime_type='application/pdf',
                    file_size_bytes=nid_saved['file_size_bytes'],
                    status=status
                )

                bar_saved = DocumentEncryptionService.save_encrypted_file(
                    SimpleUploadedFile(f"{bar_no}_BarCertificate.pdf", bar_bytes, "application/pdf"),
                    lawyer_id=str(user.id),
                    doc_type="bar_certificate"
                )
                LawyerVerificationDocument.objects.create(
                    lawyer=profile,
                    doc_type='bar_certificate',
                    file_path=bar_saved['file_path'],
                    original_filename=bar_saved['original_filename'],
                    mime_type='application/pdf',
                    file_size_bytes=bar_saved['file_size_bytes'],
                    status=status
                )
            return profile

        # 3. Create Seed Lawyers in various states:
        # A) Verified Lawyers (Display badge & visible in public search)
        create_lawyer_with_docs(
            name="Syeda Farhana Begum",
            email="s.farhana@apexlegal.bd",
            phone="+8801982441098",
            honorific="Adv.",
            headline="Senior Advocate, High Court Division",
            bar_no="SC-7841",
            bar_assoc="Supreme Court Bar Association",
            district="Dhaka",
            spec="Civil Litigation, Writ Petition",
            fee=2000.00,
            exp=14,
            status=VerificationStatus.APPROVED
        )

        create_lawyer_with_docs(
            name="Kazi Tanvir Ahmed",
            email="tanvir.ahmed@dhakabar.bd",
            phone="+8801712984511",
            honorific="Adv.",
            headline="Advocate, Dhaka Judges Court",
            bar_no="DH-9124",
            bar_assoc="Dhaka Bar Association",
            district="Dhaka",
            spec="Criminal Defense, Bail & Trial",
            fee=1200.00,
            exp=8,
            status=VerificationStatus.APPROVED
        )

        # B) Pending Verification Lawyers (HIDDEN from search; in admin review queue)
        create_lawyer_with_docs(
            name="Mahmudul Hasan",
            email="m.hasan@legalchambers.bd",
            phone="+8801811442233",
            honorific="Adv.",
            headline="Advocate, District & Sessions Court",
            bar_no="DH-4412",
            bar_assoc="Dhaka Bar Association",
            district="Dhaka",
            spec="Family Law & Child Custody",
            fee=1000.00,
            exp=5,
            status=VerificationStatus.PENDING
        )

        create_lawyer_with_docs(
            name="Nusrat Jahan",
            email="nusrat.jahan@ctgbar.bd",
            phone="+8801611778899",
            honorific="Barrister",
            headline="Barrister-at-Law, Commercial Litigation",
            bar_no="CTG-1055",
            bar_assoc="Chittagong Bar Association",
            district="Chittagong",
            spec="Corporate Law, Intellectual Property",
            fee=2500.00,
            exp=6,
            status=VerificationStatus.PENDING
        )

        # C) Rejected Lawyer (HIDDEN from search; rejected status)
        create_lawyer_with_docs(
            name="Tariqul Islam",
            email="tariqul@invalid.bd",
            phone="+8801511223344",
            honorific="Adv.",
            headline="Advocate",
            bar_no="SC-0099",
            bar_assoc="Supreme Court Bar Association",
            district="Sylhet",
            spec="Property Law",
            fee=800.00,
            exp=2,
            status=VerificationStatus.REJECTED,
            rejection_reason="Bar Council Sanad copy is illegible and could not be verified with Bar Council gazette."
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded LawAid demo accounts and lawyers!"))
