"""
Management command to seed the database with test data.
Creates leader users + 50 regular members across all categories and cities.
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.leaders.models import Leader
from apps.users.models import Membership, User

# Leader emails that should never be deleted
LEADER_EMAILS = {
    "chairman@kck.or.ke",
    "secretary@kck.or.ke",
    "treasurer@kck.or.ke",
    "welfare@kck.or.ke",
    "committee@kck.or.ke",
}

# Realistic Kenyan names
KENYAN_NAMES = [
    # Students (15)
    ("Wanjiru Kariuki", "student", "seoul", "D-2"),
    ("Brian Odhiambo", "student", "seoul", "D-2"),
    ("Faith Muthoni", "student", "busan", "D-4"),
    ("Kevin Kipchoge", "student", "seoul", "D-2"),
    ("Esther Wambui", "student", "incheon", "D-2"),
    ("Dennis Kipruto", "student", "daegu", "D-4"),
    ("Lucy Chebet", "student", "seoul", "D-2"),
    ("Victor Otieno", "student", "daejeon", "D-2"),
    ("Agnes Nyambura", "student", "gwangju", "D-4"),
    ("Samuel Korir", "student", "seoul", "D-2"),
    ("Mercy Wairimu", "student", "busan", "D-2"),
    ("Patrick Mutua", "student", "incheon", "D-4"),
    ("Janet Achieng", "student", "seoul", "D-2"),
    ("Collins Langat", "student", "daegu", "D-2"),
    ("Irene Nyokabi", "student", "seoul", "D-4"),
    # Workers (15)
    ("Joseph Maina", "worker", "seoul", "E-9"),
    ("Rose Atieno", "worker", "busan", "E-9"),
    ("Stephen Kimani", "worker", "incheon", "E-9"),
    ("Nancy Jepkosgei", "worker", "seoul", "E-9"),
    ("Michael Wafula", "worker", "daegu", "E-9"),
    ("Catherine Njoki", "worker", "busan", "E-9"),
    ("Robert Karanja", "worker", "seoul", "E-9"),
    ("Elizabeth Chelangat", "worker", "incheon", "E-9"),
    ("George Ouma", "worker", "daejeon", "E-9"),
    ("Gladys Jepchumba", "worker", "seoul", "E-9"),
    ("Francis Njenga", "worker", "busan", "H-2"),
    ("Winnie Cherotich", "worker", "gwangju", "H-2"),
    ("Henry Ngugi", "worker", "incheon", "E-9"),
    ("Alice Wangari", "worker", "seoul", "E-9"),
    ("Martin Kiptoo", "worker", "daejeon", "E-9"),
    # Professionals (12)
    ("Daniel Omondi", "professional", "seoul", "E-7"),
    ("Pauline Mwende", "professional", "seoul", "E-7"),
    ("Andrew Cheruiyot", "professional", "busan", "E-7"),
    ("Ruth Akinyi", "professional", "incheon", "E-7"),
    ("John Mutiso", "professional", "seoul", "E-7"),
    ("Christine Wanjala", "professional", "daegu", "E-7"),
    ("Thomas Kibet", "professional", "seoul", "D-8"),
    ("Monica Nduta", "professional", "daejeon", "E-7"),
    ("Philip Rotich", "professional", "incheon", "D-8"),
    ("Jacqueline Kemunto", "professional", "gwangju", "E-7"),
    ("Charles Kigen", "professional", "seoul", "E-7"),
    ("Anne Moraa", "professional", "busan", "E-7"),
    # Tourists (8)
    ("Nicholas Sang", "tourist", "seoul", "C-3"),
    ("Diana Chepchirchir", "tourist", "busan", "C-3"),
    ("Eric Mwangi", "tourist", "seoul", "C-3"),
    ("Joan Auma", "tourist", "incheon", "C-3"),
    ("Timothy Kosgei", "tourist", "daegu", "C-3"),
    ("Vivian Nekesa", "tourist", "seoul", "C-3"),
    ("Oscar Ochieng", "tourist", "daejeon", "C-3"),
    ("Lillian Jepkemoi", "tourist", "gwangju", "C-3"),
]


class Command(BaseCommand):
    help = "Seed the database with initial test data for KCK"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing non-leader users, memberships, and re-seed",
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding KCK database...")

        if options["fresh"]:
            self._clean_existing_data()

        # ---------------------------------------------------------------
        # 1. Create leader users
        # ---------------------------------------------------------------
        chairman_user = self._get_or_create_user(
            email="chairman@kck.or.ke",
            full_name="James Mwangi",
            city="seoul",
            category="professional",
            phone="+82-10-1111-0001",
            password="Chairman@2025",
            is_verified=True,
            photo="photos/james_mwangi.png",
        )

        secretary_user = self._get_or_create_user(
            email="secretary@kck.or.ke",
            full_name="Grace Wanjiku",
            city="seoul",
            category="professional",
            phone="+82-10-1111-0002",
            password="Secretary@2025",
            is_verified=True,
            photo="photos/grace_wanjiku.png",
        )

        treasurer_user = self._get_or_create_user(
            email="treasurer@kck.or.ke",
            full_name="Peter Ochieng",
            city="incheon",
            category="worker",
            phone="+82-10-1111-0003",
            password="Treasurer@2025",
            is_verified=True,
            photo="photos/peter_ochieng.png",
        )

        welfare_user = self._get_or_create_user(
            email="welfare@kck.or.ke",
            full_name="Mary Akinyi",
            city="busan",
            category="worker",
            phone="+82-10-1111-0004",
            password="Welfare@2025",
            is_verified=True,
            photo="photos/mary_akinyi.png",
        )

        committee_user = self._get_or_create_user(
            email="committee@kck.or.ke",
            full_name="David Kamau",
            city="daegu",
            category="student",
            phone="+82-10-1111-0005",
            password="Committee@2025",
            is_verified=True,
            photo="photos/david_kamau.png",
        )

        regular_user = self._get_or_create_user(
            email="member@kck.or.ke",
            full_name="Sarah Njeri",
            city="seoul",
            category="student",
            phone="+82-10-1111-0006",
            password="Member@2025",
            visa_type="D-2",
            arrival_date=date(2024, 3, 15),
        )

        # ---------------------------------------------------------------
        # 2. Create leader records
        # ---------------------------------------------------------------
        chairman_leader, created = Leader.objects.get_or_create(
            user=chairman_user,
            defaults={
                "role": "chairman",
                "title": "Chairman, Kenyan Community in Korea",
                "bio": "Serving the Kenyan diaspora in Korea since 2020.",
                "is_active": True,
                "appointed_at": timezone.now(),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  Created leader: Chairman"))

        for user_obj, role, title in [
            (secretary_user, "secretary", "General Secretary"),
            (treasurer_user, "treasurer", "Treasurer"),
            (welfare_user, "welfare", "Welfare Officer"),
            (committee_user, "committee", "Committee Member"),
        ]:
            _, created = Leader.objects.get_or_create(
                user=user_obj,
                defaults={
                    "role": role,
                    "title": title,
                    "is_active": True,
                    "appointed_by": chairman_leader,
                    "appointed_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created leader: {role}"))

        # ---------------------------------------------------------------
        # 3. Create leader memberships
        # ---------------------------------------------------------------
        today = date.today()
        for user_obj in [chairman_user, secretary_user, treasurer_user, welfare_user, committee_user]:
            Membership.objects.get_or_create(
                user=user_obj,
                status="active",
                defaults={
                    "start_date": today - timedelta(days=100),
                    "expiry_date": today + timedelta(days=265),
                    "fee_amount": 50000,
                    "currency": "KRW",
                    "payment_method": "bank_transfer",
                    "recorded_by": chairman_leader,
                },
            )

        # Pending membership for regular user
        Membership.objects.get_or_create(
            user=regular_user,
            status="pending",
            defaults={
                "start_date": today,
                "expiry_date": today + timedelta(days=365),
                "fee_amount": 50000,
                "currency": "KRW",
            },
        )

        # ---------------------------------------------------------------
        # 4. Create 50 regular Kenyan members
        # ---------------------------------------------------------------
        # Verify first 35, leave last 15 unverified
        # Create memberships for first 25
        secretary_leader = Leader.objects.get(user=secretary_user)
        created_users = []

        for idx, (name, category, city, visa) in enumerate(KENYAN_NAMES):
            email = self._name_to_email(name)
            phone = f"+82-10-{2000 + idx:04d}-{1000 + idx:04d}"

            user = self._get_or_create_user(
                email=email,
                full_name=name,
                city=city,
                category=category,
                phone=phone,
                password="Member@2025",
                visa_type=visa,
                arrival_date=today - timedelta(days=30 + idx * 7),
            )
            created_users.append(user)

        # Verify first 35
        for user in created_users[:35]:
            if not user.is_verified:
                user.is_verified = True
                user.verified_by = secretary_leader
                user.verified_at = timezone.now()
                user.save(update_fields=["is_verified", "verified_by", "verified_at", "updated_at"])

        self.stdout.write(self.style.SUCCESS(f"  Created/ensured {len(created_users)} regular members"))
        self.stdout.write(self.style.SUCCESS(f"  Verified: 35, Unverified: 15"))

        # Create active memberships for first 25
        membership_count = 0
        for user in created_users[:25]:
            _, created = Membership.objects.get_or_create(
                user=user,
                status="active",
                defaults={
                    "start_date": today - timedelta(days=50 + membership_count * 3),
                    "expiry_date": today + timedelta(days=315 - membership_count * 3),
                    "fee_amount": 50000,
                    "currency": "KRW",
                    "payment_method": "bank_transfer",
                    "payment_status": "verified",
                    "recorded_by": chairman_leader,
                },
            )
            if created:
                membership_count += 1

        self.stdout.write(self.style.SUCCESS(f"  Active memberships created: {membership_count}"))

        # ---------------------------------------------------------------
        # Summary
        # ---------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\nSeed data created successfully!"))
        self.stdout.write(f"\nTotal users: {User.objects.filter(is_deleted=False).count()}")
        self.stdout.write(f"Verified: {User.objects.filter(is_deleted=False, is_verified=True).count()}")
        self.stdout.write(f"Active memberships: {Membership.objects.filter(status='active').count()}")
        self.stdout.write("\nTest accounts:")
        self.stdout.write("  chairman@kck.or.ke  / Chairman@2025")
        self.stdout.write("  secretary@kck.or.ke / Secretary@2025")
        self.stdout.write("  treasurer@kck.or.ke / Treasurer@2025")
        self.stdout.write("  welfare@kck.or.ke   / Welfare@2025")
        self.stdout.write("  committee@kck.or.ke / Committee@2025")
        self.stdout.write("  member@kck.or.ke    / Member@2025")

    def _clean_existing_data(self):
        """Delete non-leader users and their memberships. Preserve leader users."""
        self.stdout.write("  Cleaning existing data (preserving leaders)...")
        # Delete memberships for non-leader users
        non_leader_users = User.objects.exclude(email__in=LEADER_EMAILS).exclude(email="member@kck.or.ke")
        membership_count = Membership.objects.filter(user__in=non_leader_users).count()
        Membership.objects.filter(user__in=non_leader_users).delete()
        user_count = non_leader_users.count()
        non_leader_users.delete()
        self.stdout.write(self.style.WARNING(
            f"  Deleted {user_count} users and {membership_count} memberships"
        ))

    def _get_or_create_user(self, email, full_name, city, category,
                             phone="", password="Member@2025", is_verified=False,
                             photo="", visa_type="", arrival_date=None):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "city": city,
                "category": category,
                "phone": phone,
                "is_verified": is_verified,
                "visa_type": visa_type,
                "arrival_date": arrival_date,
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"  Created user: {email}"))
        if photo:
            user.photo = photo
            user.save(update_fields=["photo"])
        return user

    @staticmethod
    def _name_to_email(name):
        parts = name.lower().split()
        return f"{parts[0]}.{parts[-1]}@kck.or.ke"
