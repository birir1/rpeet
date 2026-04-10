@extends('layouts.app')

@section('content')

<div class="container py-5">

    <!-- Section Title -->
    <div class="text-center mb-5">
        <h2 class="fw-bold">Visit Us</h2>
        <p class="text-muted">We welcome you to the Embassy. Here’s how to find us and when to visit.</p>
    </div>

    <div class="row">

        <!-- Location Info -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body">
                    <h4 class="mb-3">📍 Our Location</h4>
                    <p>
                        Embassy of Kenya<br>
                        Seoul, South Korea
                    </p>

                    <h5 class="mt-4">📞 Contact</h5>
                    <p>
                        Phone: +82-XX-XXX-XXXX<br>
                        Email: info@kenyaembassy.kr
                    </p>

                    <h5 class="mt-4">🕒 Opening Hours</h5>
                    <p>
                        Monday – Friday: 9:00 AM – 5:00 PM<br>
                        Saturday – Sunday: Closed
                    </p>
                </div>
            </div>
        </div>

        <!-- Map -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body p-0">
                    <iframe 
                        src="https://www.google.com/maps?q=Kenya+Embassy+Seoul&output=embed"
                        width="100%" 
                        height="350" 
                        style="border:0;" 
                        allowfullscreen="" 
                        loading="lazy">
                    </iframe>
                </div>
            </div>
        </div>

    </div>

    <!-- Directions -->
    <div class="mt-5">
        <div class="card shadow-sm border-0">
            <div class="card-body">
                <h4 class="mb-3">🚗 Directions</h4>
                <p>
                    The Embassy is easily accessible by public transport. You can take the subway or bus to nearby stations.
                    From there, it’s a short walk to the Embassy premises.
                </p>

                <ul>
                    <li>Nearest Subway Station: [Insert Station Name]</li>
                    <li>Bus Routes: [Insert Bus Numbers]</li>
                    <li>Parking: Available for visitors</li>
                </ul>
            </div>
        </div>
    </div>

</div>

@endsection