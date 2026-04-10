@extends('layouts.app')

@section('title', 'Apply Passport')

@section('content')

    @include('services.passport.apply.intro')
    @include('services.passport.apply.steps')
    @include('services.passport.apply.requirements')
    @include('services.passport.apply.submit')

@endsection