import os
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from accounts.models import User, UserRole, AccountStatus
from lawyers.models import LawyerProfile, LawyerVerificationDocument, VerificationStatus
from core.encryption import DocumentEncryptionService

class Command(BaseCommand):
    help = 'Seeds initial LawAid users, verified/pending lawyers, and encrypted sample documents.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding LawAid database...")

        # 1. Lead Admin
        admin, _ = User.objects.get_or_create(
            email='admin@lawaid.gov.bd',
            defaults={
                'full_name': 'Rahid Karim (Lead Administrator)',
                'role': UserRole.ADMIN,
                'phone': '+8801711000001',
                'is_staff': True,
                'is_superuser': True,
                'status': AccountStatus.ACTIVE
            }
        )
        admin.set_password('LawAid@123')
        admin.save()

        # 2. Client User
        client, _ = User.objects.get_or_create(
            email='ahnaf.shahriar@example.com',
            defaults={
                'full_name': 'Ahnaf Shahriar',
                'role': UserRole.CLIENT,
                'phone': '+8801713000021',
                'status': AccountStatus.ACTIVE
            }
        )
        client.set_password('LawAid@123')
        client.save()

        # Helper to create lawyer with encrypted documents
        def create_lawyer(name, email, phone, honorific, headline, bar_no, bar_assoc, district, spec, fee, exp, status, rejection_reason=None):
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'role': UserRole.LAWYER,
                    'phone': phone,
                    'status': AccountStatus.ACTIVE
                }
            )
            user.set_password('LawAid@123')
            user.save()

            verified_at = timezone.now() if status == VerificationStatus.APPROVED else None
            verified_by = admin if status == VerificationStatus.APPROVED else None

            profile, _ = LawyerProfile.objects.get_or_create(
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
                    'review_count': 16 if status == VerificationStatus.APPROVED else 0,
                    'bio': f"{exp}+ years practicing advocate at {bar_assoc}."
                }
            )

            # Generate sample encrypted documents
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
                    file_url=nid_saved['file_url'],
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
                    file_url=bar_saved['file_url'],
                    original_filename=bar_saved['original_filename'],
                    mime_type='application/pdf',
                    file_size_bytes=bar_saved['file_size_bytes'],
                    status=status
                )

        # A. Approved Lawyers (Visible in search with verification badge)
        create_lawyer(
            name="Rafiqul Islam",
            email="rafiqul.islam@lawaid.com.bd",
            phone="+8801712000011",
            honorific="Barrister",
            headline="Senior Advocate, Supreme Court",
            bar_no="SC-7841",
            bar_assoc="Supreme Court Bar Association",
            district="Dhaka",
            spec="Civil & Property, Constitutional / Writ",
            fee=1500.00,
            exp=18,
            status=VerificationStatus.APPROVED
        )

        create_lawyer(
            name="Nusrat Adil",
            email="nusrat.adil@lawaid.com.bd",
            phone="+8801712000012",
            honorific="Adv.",
            headline="Advocate, Dhaka District & Sessions Court",
            bar_no="DH-10492",
            bar_assoc="Dhaka Bar Association",
            district="Dhaka",
            spec="Family & Custody, Cyber Law",
            fee=800.00,
            exp=11,
            status=VerificationStatus.APPROVED
        )

        # B. Pending Lawyers (Hidden from search, pending review)
        create_lawyer(
            name="Farhan Chowdhury",
            email="farhan.chowdhury@example.com",
            phone="+8801712000016",
            honorific="Adv.",
            headline="Advocate, Dhaka Judges Court",
            bar_no="DH-4412",
            bar_assoc="Dhaka Bar Association",
            district="Dhaka",
            spec="Criminal Defense",
            fee=1000.00,
            exp=4,
            status=VerificationStatus.PENDING
        )

        # C. Rejected Lawyer (Hidden from search, rejected)
        create_lawyer(
            name="Imran Sheikh",
            email="imran.sheikh@example.com",
            phone="+8801712000017",
            honorific="Adv.",
            headline="Advocate",
            bar_no="SC-0099",
            bar_assoc="Supreme Court Bar Association",
            district="Sylhet",
            spec="Corporate Law",
            fee=1200.00,
            exp=3,
            status=VerificationStatus.REJECTED,
            rejection_reason="Bar Council Sanad copy is blurry and does not match the official Bar Council gazette."
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded LawAid demo accounts!"))
