<!-- Top Bar -->
<div style="background-color: #f5f5f5; padding: 5px 20px; font-size: 14px; display: flex; justify-content: space-between; align-items: center;">
    <div>
        📧 Email: <a href="mailto:info@example.com" style="color: #333; text-decoration: none;">info@example.com</a> | 
        ☎ Phone: <a href="tel:+1234567890" style="color: #333; text-decoration: none;">+1 234 567 890</a>
    </div>
    <div>
        <a href="#" style="margin-right: 10px; color: #333; text-decoration: none;">Login</a>
        <a href="#" style="color: #333; text-decoration: none;">Register</a>
    </div>
</div>

<!-- Main Navigation -->
<header style="background-color: #333; padding: 10px 20px;">
    <div style="display: flex; align-items: center; justify-content: space-between; color: white; flex-wrap: wrap;">
        
        <!-- Logo / Site Name -->
        <div style="font-weight: bold; font-size: 22px;">
            <a href="{{ route('home') }}" style="color: white; text-decoration: none;">
                {{ config('app.name') }}
            </a>
        </div>

        <!-- Navigation Links -->
        <nav style="display: flex; gap: 15px; flex-wrap: wrap;">

            <!-- Home / About / Contact -->
            @foreach (['home' => 'Home', 'about' => 'About', 'contact' => 'Contact'] as $route => $label)
                <a href="{{ route($route) }}" 
                   style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">{{ $label }}</a>
            @endforeach

            <!-- Visa Dropdown -->
            <div style="position: relative; display: inline-block;">
                <a href="#" style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">Visa ▾</a>
                <div style="position: absolute; background: #444; display: none; min-width: 200px; z-index: 1000;">
                    @foreach (['visitus' => 'Visit Us', 'visatypes' => 'Visa Types', 'visaissues' => 'Visa Issues', 'visaFAQs' => 'Visa FAQs', 'visaservices' => 'Visa Services'] as $page => $label)
                        <a href="{{ url('/'.$page) }}" style="color:white; display:block; padding:5px 10px; text-decoration:none;">{{ $label }}</a>
                    @endforeach
                </div>
            </div>

            <!-- Services Dropdown -->
            <div style="position: relative; display: inline-block;">
                <a href="#" style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">Services ▾</a>
                <div style="position: absolute; background: #444; display: none; min-width: 200px; z-index: 1000;">
                    @foreach (['requestapassport' => 'Request a Passport', 'howtoapplyforapassport' => 'How to Apply for Passport', 'servicesqueries' => 'Service Queries', 'serviceshighlights' => 'Service Highlights', 'applyforavisa' => 'Apply for a Visa', 'applyforscholarship' => 'Apply for Scholarship'] as $page => $label)
                        <a href="{{ url('/'.$page) }}" style="color:white; display:block; padding:5px 10px; text-decoration:none;">{{ $label }}</a>
                    @endforeach
                </div>
            </div>

            <!-- Events Dropdown -->
            <div style="position: relative; display: inline-block;">
                <a href="#" style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">Events ▾</a>
                <div style="position: absolute; background: #444; display: none; min-width: 200px; z-index: 1000;">
                    @foreach (['registerforevents'=>'Register for Events','eventhighlights'=>'Event Highlights','eventcalender'=>'Event Calendar'] as $page => $label)
                        <a href="{{ url('/'.$page) }}" style="color:white; display:block; padding:5px 10px; text-decoration:none;">{{ $label }}</a>
                    @endforeach
                </div>
            </div>

            <!-- Kenya / Culture Dropdown -->
            <div style="position: relative; display: inline-block;">
                <a href="#" style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">Discover Kenya ▾</a>
                <div style="position: absolute; background: #444; display: none; min-width: 200px; z-index: 1000;">
                    @foreach (['traveldestinations'=>'Travel Destinations','traditionsandfestivals'=>'Traditions & Festivals','kenyaswildlife'=>'Kenya’s Wildlife','culturalhighligts'=>'Cultural Highlights','calturegallery'=>'Gallery'] as $page => $label)
                        <a href="{{ url('/'.$page) }}" style="color:white; display:block; padding:5px 10px; text-decoration:none;">{{ $label }}</a>
                    @endforeach
                </div>
            </div>

            <!-- FAQs / Resources Dropdown -->
            <div style="position: relative; display: inline-block;">
                <a href="#" style="color: white; text-decoration: none; transition: color 0.3s;" 
                   onmouseover="this.style.color='#FFD700'" 
                   onmouseout="this.style.color='white'">FAQs ▾</a>
                <div style="position: absolute; background: #444; display: none; min-width: 200px; z-index: 1000;">
                    @foreach (['generalquestions'=>'General Questions','FAQs'=>'FAQs','passportFAQs'=>'Passport FAQs','consularFAQs'=>'Consular FAQs','sendusamessage'=>'Send Us a Message'] as $page => $label)
                        <a href="{{ url('/'.$page) }}" style="color:white; display:block; padding:5px 10px; text-decoration:none;">{{ $label }}</a>
                    @endforeach
                </div>
            </div>

        </nav>
    </div>
</header>

<!-- Simple JS for dropdowns -->
<script>
    document.querySelectorAll('header div[style*="inline-block"]').forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.querySelector('div').style.display = 'block';
        });
        item.addEventListener('mouseleave', () => {
            item.querySelector('div').style.display = 'none';
        });
    });
</script>