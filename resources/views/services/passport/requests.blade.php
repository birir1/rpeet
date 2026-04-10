@extends('layouts.app')

@section('title', 'Request Passport')

@section('content')

    @include('services.requests.intro')

    @include('services.requests.requirements')

    @include('services.requests.process')

    @include('services.requests.fees')

    @include('services.requests.cta')

@endsection