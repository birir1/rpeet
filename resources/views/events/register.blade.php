@extends('layouts.app')

@section('content')

<div class="container my-5">
    <h2>Register for Event</h2>

    <form>
        <div class="mb-3">
            <label>Name</label>
            <input type="text" class="form-control">
        </div>

        <div class="mb-3">
            <label>Email</label>
            <input type="email" class="form-control">
        </div>

        <button class="btn btn-success">Submit</button>
    </form>
</div>

@endsection