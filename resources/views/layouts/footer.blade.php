<!-- Footer -->
<footer style="background-color: #222; color: #fff; padding: 40px 20px; margin-top: 40px;">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; max-width: 1200px; margin: 0 auto; gap: 20px;">
        
        <!-- About / Logo -->
        <div style="flex: 1; min-width: 220px;">
            <h3 style="margin-bottom: 10px;">{{ config('app.name') }}</h3>
            <p>Welcome to {{ config('app.name') }}, your gateway to services, visas, events, and resources for Kenya.</p>
        </div>

        <!-- Quick Links -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Quick Links</h4>
            <ul style="list-style: none; padding: 0;">
                @foreach (['home' => 'Home', 'about' => 'About', 'contact' => 'Contact'] as $route => $label)
                    <li>
                        <a href="{{ route($route) }}" style="color: #fff; text-decoration: none;"
                           onmouseover="this.style.color='#FFD700'"
                           onmouseout="this.style.color='white'">
                           {{ $label }}
                        </a>
                    </li>
                @endforeach
            </ul>
        </div>

        <!-- Visa Links -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Visa</h4>
            <ul style="list-style: none; padding: 0;">
                <li><a href="{{ route('visit') }}" style="color:#fff; text-decoration:none;">Visit Us</a></li>
                <li><a href="{{ route('services.visa.types') }}" style="color:#fff; text-decoration:none;">Visa Types</a></li>
                <li><a href="{{ route('visa.services') }}" style="color:#fff; text-decoration:none;">Visa Services</a></li>
                <li><a href="{{ route('visa.issues') }}" style="color:#fff; text-decoration:none;">Visa Issues</a></li>
                <li><a href="{{ route('visa.apply') }}" style="color:#fff; text-decoration:none;">Apply Visa</a></li>
            </ul>
        </div>

        <!-- Services Links -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Services</h4>
            <ul style="list-style: none; padding: 0;">
                <li><a href="{{ route('services.passport.request') }}" style="color:#fff; text-decoration:none;">Passport Request</a></li>
                <li><a href="{{ route('services.passport.apply') }}" style="color:#fff; text-decoration:none;">Apply Passport</a></li>
                <li><a href="{{ route('services.queries') }}" style="color:#fff; text-decoration:none;">Queries</a></li>
                <li><a href="{{ route('services.highlights') }}" style="color:#fff; text-decoration:none;">Highlights</a></li>
            </ul>
        </div>

        <!-- Events / Culture / Discover -->
        <!-- Events / Culture / Discover -->
<div style="flex: 1; min-width: 180px;">
    <h4>Events & Culture</h4>
    <ul style="list-style: none; padding: 0;">

        <li><a href="{{ route('events.register') }}" style="color:#fff; text-decoration:none;">Register for Events</a></li>
        <li><a href="{{ route('events.highlights') }}" style="color:#fff; text-decoration:none;">Event Highlights</a></li>
        <li><a href="{{ route('events.calendar') }}" style="color:#fff; text-decoration:none;">Event Calendar</a></li>

        <li><a href="{{ route('kenya.discover') }}" style="color:#fff; text-decoration:none;">Travel Destinations</a></li>
        <li><a href="{{ route('kenya.discover') }}" style="color:#fff; text-decoration:none;">Traditions & Festivals</a></li>
        <li><a href="{{ route('kenya.discover') }}" style="color:#fff; text-decoration:none;">Kenya Wildlife</a></li>
        <li><a href="{{ route('kenya.discover') }}" style="color:#fff; text-decoration:none;">Cultural Highlights</a></li>

    </ul>
</div>

        <!-- FAQs & Contact -->
        <div style="flex: 1; min-width: 180px;">
            <h4>FAQs & Contact</h4>
            <ul style="list-style: none; padding: 0;">
                <li><a href="{{ route('faqs.general') }}" style="color:#fff; text-decoration:none;">General Questions</a></li>
                <li><a href="{{ route('faqs.index') }}" style="color:#fff; text-decoration:none;">All FAQs</a></li>
                <li><a href="{{ route('faqs.passport') }}" style="color:#fff; text-decoration:none;">Passport FAQs</a></li>
                <li><a href="{{ route('faqs.consular') }}" style="color:#fff; text-decoration:none;">Consular FAQs</a></li>
                <li><a href="{{ route('message') }}" style="color:#fff; text-decoration:none;">Send Us a Message</a></li>
            </ul>
        </div>

    </div>

    <!-- Contact / Social Bottom Row -->
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; max-width: 1200px; margin: 30px auto 0; border-top:1px solid #444; padding-top: 20px; font-size: 14px;">
        <div>
            📧 <a href="mailto:info@example.com" style="color:#fff; text-decoration:none;">birir.munt616@gmail.com</a> | 
            📞 <a href="tel:+1234567890" style="color:#fff; text-decoration:none;">+82 10-6692-6164</a> | 
            🏢 12 Main Street, Gwangju, South Korea
        </div>
        <div>
            <a href="#" style="color: #fff; margin-right: 10px;">Facebook</a>
            <a href="#" style="color: #fff; margin-right: 10px;">Twitter</a>
            <a href="#" style="color: #fff;">Instagram</a>
        </div>
    </div>

    <div style="text-align: center; margin-top: 20px; font-size: 14px; color: #aaa;">
        &copy; {{ date('Y') }} {{ config('app.name') }}. All rights reserved.
    </div>
</footer>