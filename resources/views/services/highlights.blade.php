@extends('layouts.app')

@section('title', 'Service Highlights')

@section('content')

    @include('services.highlights.intro')

    @include('services.highlights.features')

    @include('services.highlights.updates')

    @include('services.highlights.cta')

@endsection