<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config('app.name', 'Kenyan Community in Korea') }}</title>

    <!-- ================= BOOTSTRAP CSS ================= -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- ================= TAILWIND CSS ================= -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- ================= FONT AWESOME ================= -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <!-- ================= GOOGLE FONTS ================= -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">

    <!-- ================= CUSTOM STYLES ================= -->
    <style>
        body {
            font-family: 'Poppins', sans-serif;
        }

        .top-bar {
            background-color: #0B3D91;
            color: #fff;
            font-size: 14px;
        }

        .top-bar a {
            color: #fff;
            text-decoration: none;
        }

        .top-bar a:hover {
            color: #C8102E;
        }
    </style>

    @stack('styles')
</head>

<body>

<!-- ================= TOP BAR ================= -->
<div class="top-bar py-2 px-4 d-flex justify-content-between align-items-center flex-wrap">
    
    <!-- Contact Info -->
    {{-- <div>
        <i class="fas fa-envelope"></i>
        <a href="mailto:birir.munt616@gmail.com">birir.munt616@gmail.com</a>

        <span class="mx-2">|</span>

        <i class="fas fa-phone"></i>
        <a href="tel:+821066926164">+82 10-6692-6164</a>
    </div>

    <!-- Auth Links -->
    <div>
        <a href="#" class="me-3">Login</a>
        <a href="#">Register</a>
    </div> --}}

</div>

<!-- ================= NAVBAR INCLUDE ================= -->
@include('layouts.navbar')

<!-- ================= PAGE CONTENT ================= -->
<main>