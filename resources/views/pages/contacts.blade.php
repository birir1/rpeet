@extends('layouts.app')

@section('title', 'Contact Us')

@section('content')

    @include('pages.contact.intro')

    @include('pages.contact.reach')

    @include('pages.contact.visit')

    @include('pages.contact.message')

@endsection