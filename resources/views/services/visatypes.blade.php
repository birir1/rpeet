@extends('layouts.app')

@section('title', 'Visa Types')

@section('content')

    @include('services.visa.intro')

    @include('services.visa.categories')

    @include('services.visa.guidance')
    
    @include('services.visa.next')

@endsection