<!DOCTYPE html>
<html>
<head>
    <title>{{ config('app.name') }} - @yield('title')</title>
</head>
<body>
    @include('layouts.header') <!-- Our two-section header -->

    <div style="padding: 20px;">
        @yield('content')
    </div>

    @include('layouts.footer')
</body>
</html>