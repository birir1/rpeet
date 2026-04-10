@extends('layouts.app')

@section('title', 'About')

@section('content')

    @include('pages.about.intro')

    @include('pages.about.mission')

    @include('pages.about.history')

    @include('pages.about.leadership')

@endsection