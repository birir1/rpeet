@extends('layouts.app')

@section('title', 'Apply Visa')

@section('content')

    @include('visa.apply.intro')

    @include('visa.apply.steps')

    @include('visa.apply.requirements')

    @include('visa.apply.submit')

@endsection