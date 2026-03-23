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
                    <li><a href="{{ route($route) }}" style="color: #fff; text-decoration: none; transition: color 0.3s;"
                           onmouseover="this.style.color='#FFD700'" onmouseout="this.style.color='white'">{{ $label }}</a></li>
                @endforeach
            </ul>
        </div>

        <!-- Visa Links -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Visa</h4>
            <ul style="list-style: none; padding: 0;">
                @foreach (['visitus'=>'Visit Us','visatypes'=>'Visa Types','visaissues'=>'Visa Issues','visaFAQs'=>'Visa FAQs','visaservices'=>'Visa Services'] as $page => $label)
                    <li><a href="{{ url('/'.$page) }}" style="color:#fff; text-decoration:none; transition: color 0.3s;"
                           onmouseover="this.style.color='#FFD700'" onmouseout="this.style.color='white'">{{ $label }}</a></li>
                @endforeach
            </ul>
        </div>

        <!-- Services Links -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Services</h4>
            <ul style="list-style: none; padding: 0;">
                @foreach (['requestapassport'=>'Request a Passport','howtoapplyforapassport'=>'How to Apply','servicesqueries'=>'Service Queries','serviceshighlights'=>'Service Highlights','applyforavisa'=>'Apply for a Visa','applyforscholarship'=>'Apply for Scholarship'] as $page => $label)
                    <li><a href="{{ url('/'.$page) }}" style="color:#fff; text-decoration:none; transition: color 0.3s;"
                           onmouseover="this.style.color='#FFD700'" onmouseout="this.style.color='white'">{{ $label }}</a></li>
                @endforeach
            </ul>
        </div>

        <!-- Events / Culture / FAQs -->
        <div style="flex: 1; min-width: 180px;">
            <h4>Events & Culture</h4>
            <ul style="list-style: none; padding: 0;">
                @foreach (['registerforevents'=>'Register for Events','eventhighlights'=>'Event Highlights','eventcalender'=>'Event Calendar','traveldestinations'=>'Travel Destinations','traditionsandfestivals'=>'Traditions & Festivals','kenyaswildlife'=>'Kenya Wildlife','culturalhighligts'=>'Cultural Highlights','calturegallery'=>'Gallery'] as $page => $label)
                    <li><a href="{{ url('/'.$page) }}" style="color:#fff; text-decoration:none; transition: color 0.3s;"
                           onmouseover="this.style.color='#FFD700'" onmouseout="this.style.color='white'">{{ $label }}</a></li>
                @endforeach
            </ul>
        </div>

        <!-- FAQs & Contact -->
        <div style="flex: 1; min-width: 180px;">
            <h4>FAQs & Contact</h4>
            <ul style="list-style: none; padding: 0;">
                @foreach (['generalquestions'=>'General Questions','FAQs'=>'FAQs','passportFAQs'=>'Passport FAQs','consularFAQs'=>'Consular FAQs','sendusamessage'=>'Send Us a Message'] as $page => $label)
                    <li><a href="{{ url('/'.$page) }}" style="color:#fff; text-decoration:none; transition: color 0.3s;"
                           onmouseover="this.style.color='#FFD700'" onmouseout="this.style.color='white'">{{ $label }}</a></li>
                @endforeach
            </ul>
        </div>

    </div>

    <!-- Contact / Social Bottom Row -->
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; max-width: 1200px; margin: 30px auto 0; border-top:1px solid #444; padding-top: 20px; font-size: 14px;">
        <div>
            📧 <a href="mailto:info@example.com" style="color:#fff; text-decoration:none;">info@example.com</a> | 
            📞 <a href="tel:+1234567890" style="color:#fff; text-decoration:none;">+1 234 567 890</a> | 
            🏢 123 Main Street, City, Country
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