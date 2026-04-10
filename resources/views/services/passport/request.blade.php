@extends('layouts.app')

@section('title', 'Request Passport')

@section('content')

    @include('services.passport.request.intro')
    @include('services.passport.request.eligibility')
    @include('services.passport.request.process')
    @include('services.passport.request.cta')

@endsection