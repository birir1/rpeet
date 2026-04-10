@extends('layouts.app')

@section('title', 'Home')

@section('content')

    @include('frontend.sendusamessage')
    
    @include('frontend.ourlocation')

    @include('frontend.openinghours')

    {{-- @include('frontend.visitus') --}}

@endsection