<!-- ================= TOP BAR ================= -->
<section id="top-bar">
    <div style="background-color: #0B3D91; color: #fff; padding: 5px 20px; font-size: 14px; display: flex; justify-content: space-between; align-items: center;">
        
        <div>
            📧 <a href="mailto:birir.munt616@gmail.com" style="color:#fff; text-decoration:none;">birir.munt616@gmail.com</a> |
            ☎ <a href="tel:+821066926164" style="color:#fff; text-decoration:none;">+82 10-6692-6164</a>
        </div>

        <div>
            <a href="#" style="color:#fff; margin-right:10px; text-decoration:none;">Login</a>
            <a href="#" style="color:#fff; text-decoration:none;">Register</a>
        </div>

    </div>
</section>


<!-- ================= MAIN NAVBAR ================= -->
<section id="main-navbar">
<header style="background-color: #000; border-bottom: 3px solid #C8102E; padding: 10px 20px;">

    <div style="display: flex; flex-direction: column; align-items: center; color:white;">

        <!-- ================= LOGO ================= -->
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">
            <a href="{{ route('home') }}" style="color:#fff; text-decoration:none;">
                {{ config('app.name') }}
            </a>
        </div>

        <!-- ================= NAVIGATION ================= -->
        <nav style="
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            flex-wrap: wrap;
            font-size: 18px;
            width: 100%;
            max-width: 1100px;
        ">

            <!-- ================= BASIC LINKS ================= -->
            <section id="nav-basic" style="display:flex; gap:20px;">
                <a href="{{ route('home') }}" style="color:#fff; text-decoration:none;">Home</a>
                <a href="{{ route('about') }}" style="color:#fff; text-decoration:none;">About</a>
                <a href="{{ route('contact') }}" style="color:#fff; text-decoration:none;">Contact</a>
            </section>


            <!-- ================= VISA ================= -->
            <section id="nav-visa" class="dropdown">
                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    Visa
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('visit') }}" style="color:#fff; text-decoration:none;">Visit Us</a>
                    <a class="dropdown-item" href="{{ route('services.visa.types') }}" style="color:#fff; text-decoration:none;">Visa Types</a>
                    <a class="dropdown-item" href="{{ route('visa.services') }}" style="color:#fff; text-decoration:none;">Visa Services</a>
                    <a class="dropdown-item" href="{{ route('visa.issues') }}" style="color:#fff; text-decoration:none;">Visa Issues</a>
                    <a class="dropdown-item" href="{{ route('faqs.index') }}" style="color:#fff; text-decoration:none;">Visa FAQs</a>
                    <a class="dropdown-item" href="{{ route('visa.apply') }}" style="color:#fff; text-decoration:none;">Apply Visa</a>
                </div>
            </section>


            <!-- ================= SERVICES ================= -->
            <section id="nav-services" class="dropdown">
                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    Services
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('services.passport.request') }}" style="color:#fff; text-decoration:none;">Request Passport</a>
                    <a class="dropdown-item" href="{{ route('services.passport.apply') }}" style="color:#fff; text-decoration:none;">Apply Passport</a>
                    <a class="dropdown-item" href="{{ route('services.queries') }}" style="color:#fff; text-decoration:none;">Queries</a>
                    <a class="dropdown-item" href="{{ route('services.highlights') }}" style="color:#fff; text-decoration:none;">Highlights</a>
                    <a class="dropdown-item" href="{{ route('visa.apply') }}" style="color:#fff; text-decoration:none;">Apply Visa</a>
                </div>
            </section>


            <!-- ================= EVENTS ================= -->
            <section id="nav-events" class="dropdown">
                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    Events
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('events') }}" style="color:#fff; text-decoration:none;">All Events</a>
                    <a class="dropdown-item" href="{{ route('events.register') }}" style="color:#fff; text-decoration:none;">Register</a>
                    <a class="dropdown-item" href="{{ route('events.calendar') }}" style="color:#fff; text-decoration:none;">Calendar</a>
                    <a class="dropdown-item" href="{{ route('events.highlights') }}" style="color:#fff; text-decoration:none;">Highlights</a>
                </div>
            </section>


            <!-- ================= DISCOVER ================= -->
            <section id="nav-discover" class="dropdown">
                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    Discover
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('kenya.discover') }}" style="color:#fff; text-decoration:none;">
                        Discover Kenya
                    </a>
                </div>
            </section>


            <!-- ================= COMMUNITY ================= -->
            <section id="nav-community" class="dropdown">

                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    Community
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('community.history') }}" style="color:#fff;">History</a>
                    <a class="dropdown-item" href="{{ route('community.location') }}" style="color:#fff;">Location</a>
                    <a class="dropdown-item" href="{{ route('community.hours') }}" style="color:#fff;">Opening Hours</a>
                    <a class="dropdown-item" href="{{ route('community.mission') }}" style="color:#fff;">Mission</a>
                    <a class="dropdown-item" href="{{ route('community.vision') }}" style="color:#fff;">Vision</a>
                </div>
            </section>


            <!-- ================= FAQ ================= -->
            <section id="nav-faq" class="dropdown">

                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown" style="color:#fff; text-decoration:none;">
                    FAQs
                </a>

                <div class="dropdown-menu" style="background:#0B3D91; font-size:16px;">
                    <a class="dropdown-item" href="{{ route('faqs.index') }}" style="color:#fff;">
                        All FAQs
                    </a>
                    <a class="dropdown-item" href="{{ route('faqs.general') }}" style="color:#fff;">
                        General
                    </a>
                    <a class="dropdown-item" href="{{ route('faqs.passport') }}" style="color:#fff;">
                        Passport
                    </a>
                    <a class="dropdown-item" href="{{ route('faqs.consular') }}" style="color:#fff;">
                        Consular
                    </a>
                    <a class="dropdown-item" href="{{ route('message') }}" style="color:#fff;">
                        Send Message
                    </a>
                </div>
            </section>

        </nav>
    </div>
</header>
</section>