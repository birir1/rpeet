@extends('layouts.app')

@section('title', 'Service Queries')

@section('content')

    @include('services.queries.intro')

    @include('services.queries.options')

    @include('services.queries.form')

    @include('services.queries.contact')

@endsection