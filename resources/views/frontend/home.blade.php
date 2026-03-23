@extends('layouts.app')

@section('title', 'Home')

@section('content')
    <h1>Welcome to {{ config('app.name') }}</h1>
    <p>This is the home page.</p>
@endsection