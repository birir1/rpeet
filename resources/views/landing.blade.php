<!-- ================= LANDING / HERO SECTION ================= -->
<section style="
    background: linear-gradient(rgba(11,61,145,0.85), rgba(0,0,0,0.85)),
                url('https://images.unsplash.com/photo-1547471080-7cc2caa01a7e');
    background-size: cover;
    background-position: center;
    color: #fff;
    padding: 100px 20px;
    text-align: center;
">

    <div style="max-width: 900px; margin: 0 auto;">

        <!-- Title -->
        <h1 style="font-size: 48px; font-weight: bold; margin-bottom: 20px;">
            Welcome to {{ config('app.name') }}
        </h1>

        <!-- Subtitle -->
        <p style="font-size: 18px; line-height: 1.6; margin-bottom: 30px;">
            Your gateway to Kenyan services, visas, culture, and community in South Korea.
            Access everything you need — fast, simple, and reliable.
        </p>

        <!-- Call to Action Buttons -->
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            
            <a href="/applyforavisa" 
               style="background-color:#C8102E; color:#fff; padding:12px 25px; text-decoration:none; border-radius:5px; font-weight:bold;">
                Apply for Visa
            </a>

            <a href="/requestapassport" 
               style="background-color:#fff; color:#000; padding:12px 25px; text-decoration:none; border-radius:5px; font-weight:bold;">
                Passport Services
            </a>

        </div>

    </div>

</section>