@extends('layouts.app')

@section('title', 'Home')

@section('content')

    @include('pages.home.sections.hero')

    @include('pages.home.sections.services')

    @include('pages.home.sections.discover')

    @include('pages.home.sections.community')

@endsection