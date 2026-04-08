"""
Management command to seed the database with test data.
Creates leader users + 50 regular members across all categories and cities,
plus events, announcements, communications, and certificates so the frontend
developer has realistic data to build against.
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.certificates.models import Certificate
from apps.communications.models import Announcement, Communication
from apps.events.models import Event, EventAttendee
from apps.leaders.models import Leader
from apps.users.models import Membership, User

# Leader emails that should never be deleted
LEADER_EMAILS = {
    "president@kenyakorea.com",
    "secgen@kenyakorea.com",
    "finance@kenyakorea.com",
    "welfare@kenyakorea.com",
    "committee@kenyakorea.com",
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
            email="president@kenyakorea.com",
            full_name="James Mwangi",
            city="seoul",
            category="professional",
            phone="+82-10-1111-0001",
            password="Chairman@2025",
            is_verified=True,
            photo="photos/james_mwangi.png",
        )

        secretary_user = self._get_or_create_user(
            email="secgen@kenyakorea.com",
            full_name="Grace Wanjiku",
            city="seoul",
            category="professional",
            phone="+82-10-1111-0002",
            password="Secretary@2025",
            is_verified=True,
            photo="photos/grace_wanjiku.png",
        )

        treasurer_user = self._get_or_create_user(
            email="finance@kenyakorea.com",
            full_name="Peter Ochieng",
            city="incheon",
            category="worker",
            phone="+82-10-1111-0003",
            password="Treasurer@2025",
            is_verified=True,
            photo="photos/peter_ochieng.png",
        )

        welfare_user = self._get_or_create_user(
            email="welfare@kenyakorea.com",
            full_name="Mary Akinyi",
            city="busan",
            category="worker",
            phone="+82-10-1111-0004",
            password="Welfare@2025",
            is_verified=True,
            photo="photos/mary_akinyi.png",
        )

        committee_user = self._get_or_create_user(
            email="committee@kenyakorea.com",
            full_name="David Kamau",
            city="daegu",
            category="student",
            phone="+82-10-1111-0005",
            password="Committee@2025",
            is_verified=True,
            photo="photos/david_kamau.png",
        )

        regular_user = self._get_or_create_user(
            email="member@kenyakorea.com",
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
        # 5. Create events (past + upcoming)
        # ---------------------------------------------------------------
        committee_leader = Leader.objects.get(user=committee_user)
        events_data = [
            {
                "title": "KCK Annual General Meeting 2026",
                "excerpt": "Our yearly gathering to review community achievements, elect new leaders, and plan the year ahead.",
                "body": "<p>Dear KCK members,</p><p>We are pleased to invite all Kenyans in Korea to our Annual General Meeting. This is our most important meeting of the year where we review achievements, present financial reports, and set priorities for the coming year.</p><h3>Agenda</h3><ul><li>Welcome remarks by the Chairman</li><li>Secretary General's report</li><li>Treasurer's financial report</li><li>Welfare Officer's report</li><li>Committee member reports</li><li>Open discussion and Q&A</li><li>Refreshments and networking</li></ul><p><strong>Please RSVP by April 20th.</strong> Light refreshments will be served.</p>",
                "event_date": today + timedelta(days=15),
                "location": "Seoul Global Center, Jongno-gu, Seoul",
                "is_published": True,
            },
            {
                "title": "Kenyan Cultural Night — Taste of Home",
                "excerpt": "Come celebrate Kenyan culture with traditional food, music, dance, and storytelling. All welcome!",
                "body": "<p>Get ready for an unforgettable evening celebrating Kenyan heritage! Join us for an authentic taste of home with traditional dishes, live music, cultural performances, and plenty of nostalgic conversations.</p><h3>What to expect</h3><ul><li><strong>Authentic Kenyan cuisine:</strong> ugali, nyama choma, sukuma wiki, chapati, pilau, mandazi, and more</li><li><strong>Live music:</strong> benga, taarab, and afro-fusion</li><li><strong>Cultural dances:</strong> traditional dances from different Kenyan communities</li><li><strong>Storytelling corner:</strong> share your Korea experiences</li><li><strong>Kids' activities</strong> for the little ones</li></ul><p>Entry: Free for KCK members, 10,000 KRW for guests.</p>",
                "event_date": today + timedelta(days=45),
                "location": "Itaewon Global Village Center, Yongsan-gu, Seoul",
                "is_published": True,
            },
            {
                "title": "Kenya Independence Day Celebration (Jamhuri Day)",
                "excerpt": "Join the KCK community to celebrate Kenya's independence with flag-raising, speeches, and fellowship.",
                "body": "<p>On December 12th, Kenyans worldwide celebrate Jamhuri Day — the day our nation gained independence in 1963. Join the Kenyan Community in Korea as we honor our history and look forward to our future.</p><h3>Programme</h3><ul><li>9:00 AM — Flag-raising ceremony</li><li>9:30 AM — National anthem and opening prayer</li><li>10:00 AM — Keynote address by the Chairman</li><li>10:30 AM — Cultural performances</li><li>12:00 PM — Traditional Kenyan lunch</li><li>2:00 PM — Games and fellowship</li></ul><p>Dress code: Kenyan national colors or traditional attire encouraged.</p>",
                "event_date": today + timedelta(days=90),
                "location": "Seoul Plaza, Jung-gu, Seoul",
                "is_published": True,
            },
            {
                "title": "Community Health & Wellness Workshop",
                "excerpt": "Free health screening, wellness tips, and mental health awareness for all KCK members and families.",
                "body": "<p>Your health is your wealth. Join us for a comprehensive health and wellness workshop designed specifically for the Kenyan community in Korea.</p><h3>What's included</h3><ul><li><strong>Free health screening:</strong> blood pressure, blood sugar, BMI</li><li><strong>Nutrition talk:</strong> healthy eating on a Korean budget</li><li><strong>Mental health awareness:</strong> coping with homesickness and culture shock</li><li><strong>Korean healthcare navigation:</strong> how to use national health insurance</li><li><strong>Q&A with Kenyan medical professionals</strong></li></ul><p>All services are free and confidential.</p>",
                "event_date": today + timedelta(days=25),
                "location": "Ansan Multicultural Center, Ansan",
                "is_published": True,
            },
            {
                "title": "Youth Networking Mixer — Build Your Network",
                "excerpt": "Young Kenyan professionals and students — come network, share opportunities, and build lasting friendships.",
                "body": "<p>Are you a young Kenyan student or professional in Korea? This mixer is for you! Build your network, share opportunities, and connect with peers who understand your journey.</p><h3>Programme</h3><ul><li>Speed networking session</li><li>Lightning talks from successful Kenyans in Korea</li><li>Career panel discussion</li><li>Open mingling with refreshments</li></ul><p>Bring your business cards and an open mind!</p>",
                "event_date": today + timedelta(days=35),
                "location": "Gangnam Startup Campus, Gangnam-gu, Seoul",
                "is_published": True,
            },
            {
                "title": "KCK Football Tournament 2025",
                "excerpt": "Our annual football tournament brought together teams from across Korea for a day of sport and fellowship.",
                "body": "<p>What a day it was! Over 80 players from 6 teams representing Seoul, Busan, Incheon, Daegu, Daejeon, and Gwangju came together for our annual KCK Football Tournament.</p><h3>Results</h3><ul><li><strong>1st place:</strong> Seoul Warriors</li><li><strong>2nd place:</strong> Busan Lions</li><li><strong>3rd place:</strong> Incheon Eagles</li></ul><p>Thank you to everyone who participated, supported, and cheered. See you next year!</p>",
                "event_date": today - timedelta(days=60),
                "location": "Seoul World Cup Stadium Auxiliary Ground",
                "is_published": True,
            },
            {
                "title": "New Year Welcome Reception 2026",
                "excerpt": "Ring in the new year with the KCK community over good food, good music, and great company.",
                "body": "<p>We kicked off 2026 with style! Our New Year Welcome Reception brought together over 120 Kenyans from across Korea for an evening of celebration, reflection, and forward-looking resolutions.</p><p>Thank you to everyone who made it special, especially our volunteers and sponsors.</p>",
                "event_date": today - timedelta(days=90),
                "location": "Lotte Hotel Seoul",
                "is_published": True,
            },
        ]

        events_created = 0
        for ev_data in events_data:
            event, created = Event.objects.get_or_create(
                title=ev_data["title"],
                defaults={
                    **ev_data,
                    "created_by": committee_leader,
                },
            )
            if created:
                events_created += 1

        self.stdout.write(self.style.SUCCESS(f"  Events created: {events_created}"))

        # Add attendees to past events
        past_events = Event.objects.filter(event_date__lt=today)
        for event in past_events:
            # Add 10-15 attendees from created users
            for user in created_users[:12]:
                EventAttendee.objects.get_or_create(
                    event=event,
                    user=user,
                    defaults={
                        "name": user.full_name,
                        "email": user.email,
                        "attended": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"  Event attendees added to past events"))

        # ---------------------------------------------------------------
        # 6. Create announcements
        # ---------------------------------------------------------------
        announcements_data = [
            {
                "title": "Welcome to the Kenya Community in Korea",
                "body": "<p>Karibu! Welcome to the official online home of the Kenya Community in Korea (KCK). Whether you're a student, worker, professional, or visitor, this platform is your gateway to connecting with fellow Kenyans across South Korea.</p><p>Register for membership, stay updated on events, access community resources, and build lifelong friendships. We're here to make Korea feel a little more like home.</p>",
                "category": "general",
                "author": chairman_leader,
            },
            {
                "title": "Annual Membership Renewals Now Open",
                "body": "<p>Dear members, it's that time of the year again. Annual membership renewals for 2026 are now open. The membership fee remains at <strong>50,000 KRW per year</strong>.</p><p>Your membership supports community events, welfare initiatives, and operational costs. To renew, log in to your portal and follow the instructions under the Membership tab. Thank you for your continued support.</p>",
                "category": "notice",
                "author": treasurer_user.leader if hasattr(treasurer_user, 'leader') else chairman_leader,
            },
            {
                "title": "In Loving Memory — Mama Rebecca Wanjiru",
                "body": "<p>It is with deep sorrow that we announce the passing of Mama Rebecca Wanjiru, mother to our beloved member Wanjiru Kariuki. Mama Rebecca was a pillar in her community and her warmth touched many.</p><p>The KCK family stands with Wanjiru and her family during this difficult time. Condolence contributions can be sent through the Welfare Officer. Funeral details will be shared once confirmed.</p><p>May her soul rest in eternal peace. <em>Pumzika kwa amani.</em></p>",
                "category": "condolence",
                "author": welfare_user.leader if hasattr(welfare_user, 'leader') else chairman_leader,
            },
            {
                "title": "Congratulations to Our Newest Graduates!",
                "body": "<p>We are thrilled to congratulate members of the KCK family who have recently graduated from various Korean universities:</p><ul><li><strong>Kevin Kipchoge</strong> — Master's in Computer Science, Seoul National University</li><li><strong>Esther Wambui</strong> — Bachelor's in Business Administration, Yonsei University</li><li><strong>Dennis Kipruto</strong> — PhD in Mechanical Engineering, KAIST</li></ul><p>Your hard work, dedication, and resilience are an inspiration to us all. Congratulations and all the best in your next chapter!</p>",
                "category": "celebration",
                "author": chairman_leader,
            },
            {
                "title": "URGENT: Update on Visa Policy Changes",
                "body": "<p><strong>Important notice for D-2 and E-9 visa holders:</strong></p><p>The Korean Ministry of Justice has announced updates to visa renewal procedures effective next month. Please review the changes on the official immigration website or contact our Secretary General for guidance.</p><p>KCK will host an information session next week to help members navigate these changes. Details will be shared soon.</p>",
                "category": "notice",
                "author": secretary_user.leader if hasattr(secretary_user, 'leader') else chairman_leader,
            },
            {
                "title": "Welfare Support Available — Don't Suffer in Silence",
                "body": "<p>The KCK Welfare Committee is here for you during difficult times. We provide support for:</p><ul><li>Medical emergencies and hospital bills</li><li>Bereavement support</li><li>Temporary financial assistance</li><li>Mental health resources and counseling referrals</li><li>Legal aid connections</li></ul><p>All requests are handled confidentially. Contact our Welfare Officer directly or submit a request through the portal. You are not alone.</p>",
                "category": "welfare",
                "author": welfare_user.leader if hasattr(welfare_user, 'leader') else chairman_leader,
            },
            {
                "title": "Cultural Night Tickets Now Available",
                "body": "<p>Tickets for our upcoming Kenyan Cultural Night are now available! Don't miss an unforgettable evening of food, music, dance, and fellowship.</p><p><strong>Members:</strong> Free entry<br><strong>Non-members:</strong> 10,000 KRW</p><p>RSVP through the portal or contact any committee member. Limited seats — first come, first served.</p>",
                "category": "event",
                "author": committee_leader,
            },
            {
                "title": "Office Hours Update",
                "body": "<p>Please note that the KCK office hours have been updated for 2026:</p><ul><li><strong>Monday - Friday:</strong> 10:00 AM - 6:00 PM</li><li><strong>Saturday:</strong> 10:00 AM - 2:00 PM (by appointment)</li><li><strong>Sunday:</strong> Closed</li></ul><p>For urgent matters outside office hours, please contact the Secretary General directly.</p>",
                "category": "general",
                "author": secretary_user.leader if hasattr(secretary_user, 'leader') else chairman_leader,
            },
        ]

        announcements_created = 0
        for ann_data in announcements_data:
            _, created = Announcement.objects.get_or_create(
                title=ann_data["title"],
                defaults={
                    **ann_data,
                    "is_published": True,
                },
            )
            if created:
                announcements_created += 1

        self.stdout.write(self.style.SUCCESS(f"  Announcements created: {announcements_created}"))

        # ---------------------------------------------------------------
        # 7. Create communications (official letters)
        # ---------------------------------------------------------------
        communications_data = [
            {
                "subject": "Notice of Annual General Meeting",
                "body": "<p>Dear esteemed members,</p><p>This is to formally notify you of the upcoming Annual General Meeting of the Kenya Community in Korea. The meeting will take place on the date specified in our events page.</p><p>All verified members are encouraged to attend as important matters concerning our community will be discussed and voted upon.</p><p>Yours in service,<br>James Mwangi<br>Chairman, KCK</p>",
                "category": "general",
                "audience": "members_only",
                "sender": chairman_leader,
                "status": "published",
            },
            {
                "subject": "Membership Renewal Reminder",
                "body": "<p>Dear member,</p><p>This is a friendly reminder that your annual membership is due for renewal. Please renew through the portal or contact the Treasurer for assistance.</p><p>Thank you for being part of our community.</p><p>Peter Ochieng<br>Treasurer, KCK</p>",
                "category": "general",
                "audience": "members_only",
                "sender": treasurer_user.leader if hasattr(treasurer_user, 'leader') else chairman_leader,
                "status": "published",
            },
            {
                "subject": "Welfare Fund Appeal — Support One of Our Own",
                "body": "<p>Dear KCK family,</p><p>We are reaching out to request your support for a fellow member facing significant medical expenses. In the spirit of ubuntu — I am because we are — let us come together to support our own.</p><p>Contributions can be sent to the Welfare Fund account. Every shilling counts.</p><p>Asante sana.<br>Mary Akinyi<br>Welfare Officer</p>",
                "category": "welfare",
                "audience": "all",
                "sender": welfare_user.leader if hasattr(welfare_user, 'leader') else chairman_leader,
                "status": "published",
            },
            {
                "subject": "EMERGENCY: Earthquake Safety Advisory",
                "body": "<p>Dear members,</p><p>Following recent seismic activity, we advise all members to familiarize themselves with Korea's earthquake safety protocols. Know your nearest evacuation center and keep an emergency kit ready.</p><p>Register for emergency alerts through the Safety Korea app. Stay safe.</p>",
                "category": "emergency",
                "audience": "all",
                "sender": secretary_user.leader if hasattr(secretary_user, 'leader') else chairman_leader,
                "status": "published",
            },
        ]

        comms_created = 0
        for comm_data in communications_data:
            _, created = Communication.objects.get_or_create(
                subject=comm_data["subject"],
                defaults={
                    **comm_data,
                    "published_at": timezone.now(),
                },
            )
            if created:
                comms_created += 1

        self.stdout.write(self.style.SUCCESS(f"  Communications created: {comms_created}"))

        # ---------------------------------------------------------------
        # 8. Create sample certificates
        # ---------------------------------------------------------------
        cert_samples = [
            {
                "recipient_name": "Kevin Kipchoge",
                "recipient_user": next((u for u in created_users if "kevin" in u.email.lower()), None),
                "cert_type": "appreciation",
                "body": "In recognition of outstanding contribution to the Kenya Community in Korea through tireless volunteer work during the 2025 cultural festival.",
            },
            {
                "recipient_name": "Esther Wambui",
                "recipient_user": next((u for u in created_users if "esther" in u.email.lower()), None),
                "cert_type": "leadership",
                "body": "For exceptional leadership as Chair of the KCK Youth Committee 2025, fostering unity and growth among young Kenyans in Korea.",
            },
            {
                "recipient_name": "Dennis Kipruto",
                "recipient_user": next((u for u in created_users if "dennis" in u.email.lower()), None),
                "cert_type": "participation",
                "body": "For active participation in the KCK Football Tournament 2025, demonstrating sportsmanship and community spirit.",
            },
            {
                "recipient_name": "Faith Muthoni",
                "recipient_user": next((u for u in created_users if "faith" in u.email.lower()), None),
                "cert_type": "welfare",
                "body": "In grateful recognition of generous contributions to the KCK Welfare Fund supporting members in need.",
            },
            {
                "recipient_name": "Brian Odhiambo",
                "recipient_user": next((u for u in created_users if "brian" in u.email.lower()), None),
                "cert_type": "appreciation",
                "body": "For outstanding service as event coordinator for the New Year Welcome Reception 2026.",
            },
        ]

        certs_created = 0
        for cert_data in cert_samples:
            _, created = Certificate.objects.get_or_create(
                recipient_name=cert_data["recipient_name"],
                cert_type=cert_data["cert_type"],
                defaults={
                    "recipient_user": cert_data["recipient_user"],
                    "body": cert_data["body"],
                    "issued_by": chairman_leader,
                    "status": "draft",
                },
            )
            if created:
                certs_created += 1

        self.stdout.write(self.style.SUCCESS(f"  Certificates created: {certs_created}"))

        # ---------------------------------------------------------------
        # Summary
        # ---------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\nSeed data created successfully!"))
        self.stdout.write(f"\nTotal users: {User.objects.filter(is_deleted=False).count()}")
        self.stdout.write(f"Verified: {User.objects.filter(is_deleted=False, is_verified=True).count()}")
        self.stdout.write(f"Active memberships: {Membership.objects.filter(status='active').count()}")
        self.stdout.write(f"Events: {Event.objects.count()}")
        self.stdout.write(f"Announcements: {Announcement.objects.count()}")
        self.stdout.write(f"Communications: {Communication.objects.count()}")
        self.stdout.write(f"Certificates: {Certificate.objects.count()}")
        self.stdout.write("\nTest accounts:")
        self.stdout.write("  president@kenyakorea.com  / Chairman@2025")
        self.stdout.write("  secgen@kenyakorea.com / Secretary@2025")
        self.stdout.write("  finance@kenyakorea.com / Treasurer@2025")
        self.stdout.write("  welfare@kenyakorea.com   / Welfare@2025")
        self.stdout.write("  committee@kenyakorea.com / Committee@2025")
        self.stdout.write("  member@kenyakorea.com    / Member@2025")

    def _clean_existing_data(self):
        """Delete non-leader users and their memberships. Preserve leader users."""
        self.stdout.write("  Cleaning existing data (preserving leaders)...")
        # Delete memberships for non-leader users
        non_leader_users = User.objects.exclude(email__in=LEADER_EMAILS).exclude(email="member@kenyakorea.com")
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
        return f"{parts[0]}.{parts[-1]}@kenyakorea.com"
