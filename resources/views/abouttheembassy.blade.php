<!DOCTYPE html>
<html>
<head>
    <title>{{ config('app.name') }} - @yield('title')</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
    @include('layouts.header') <!-- Our two-section header -->

    <div style="padding: 20px;">
        @yield('content')
    </div>

    {{-- @include('frontend.ourmissioninkorea')

    @include('frontend.contactus') --}}

    @include('layouts.footer')
</body>
</html>