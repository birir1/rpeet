@extends('layouts.app')

@section('title', 'Visa FAQs')

@section('content')

    @include('visa.faqs.intro')

    @include('visa.faqs.questions')

    @include('visa.faqs.categories')

    @include('visa.faqs.contact')

@endsection