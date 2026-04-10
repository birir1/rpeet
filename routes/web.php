<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PageController;

/*
|--------------------------------------------------------------------------
| MAIN PAGES
|--------------------------------------------------------------------------
*/
Route::get('/', [PageController::class, 'home'])->name('home');
Route::get('/about', [PageController::class, 'about'])->name('about');
Route::get('/contact', [PageController::class, 'contact'])->name('contact');


/*
|--------------------------------------------------------------------------
| EMBASSY
|--------------------------------------------------------------------------
*/
Route::prefix('embassy')->group(function () {
    Route::get('/ambassador', [PageController::class, 'ambassador'])->name('embassy.ambassador');
    Route::get('/history', [PageController::class, 'embassyHistory'])->name('embassy.history');
});


/*
|--------------------------------------------------------------------------
| VISIT
|--------------------------------------------------------------------------
*/
Route::get('/visit', [PageController::class, 'visitus'])->name('visit');


/*
|--------------------------------------------------------------------------
| VISA
|--------------------------------------------------------------------------
*/
Route::prefix('visa')->group(function () {
    Route::get('/types', [PageController::class, 'visatypes'])->name('visa.types');
    Route::get('/services', [PageController::class, 'visaservices'])->name('visa.services');
    Route::get('/issues', [PageController::class, 'visaissues'])->name('visa.issues');

    Route::get('/faqs', [PageController::class, 'faqs'])->name('visa.faqs');

    Route::get('/apply', function () {
        return redirect()->route('visa.services');
    })->name('visa.apply');
});


/*
|--------------------------------------------------------------------------
| SERVICES
|--------------------------------------------------------------------------
*/
Route::prefix('services')->group(function () {
    Route::get('/visa-types', [PageController::class, 'visatypes'])->name('services.visa.types');

    Route::get('/passport-request', [PageController::class, 'passportRequest'])->name('services.passport.request');
    Route::get('/passport-apply', [PageController::class, 'passportApply'])->name('services.passport.apply');
    Route::get('/queries', [PageController::class, 'queries'])->name('services.queries');
    Route::get('/highlights', [PageController::class, 'highlights'])->name('services.highlights');
});


/*
|--------------------------------------------------------------------------
| KENYA / DISCOVER
|--------------------------------------------------------------------------
*/
Route::prefix('kenya')->group(function () {
    Route::get('/discover', [PageController::class, 'discover'])->name('kenya.discover');
});


/*
|--------------------------------------------------------------------------
| COMMUNITY
|--------------------------------------------------------------------------
*/
Route::prefix('community')->group(function () {
    Route::get('/', [PageController::class, 'communityIndex'])->name('community.index');
    Route::get('/history', [PageController::class, 'communityHistory'])->name('community.history');
    Route::get('/location', [PageController::class, 'location'])->name('community.location');
    Route::get('/hours', [PageController::class, 'hours'])->name('community.hours');
    Route::get('/mission', [PageController::class, 'mission'])->name('community.mission');
    Route::get('/vision', [PageController::class, 'vision'])->name('community.vision');
});


/*
|--------------------------------------------------------------------------
| EVENTS
|--------------------------------------------------------------------------
*/
Route::prefix('events')->group(function () {
    Route::get('/', [PageController::class, 'events'])->name('events');
    Route::get('/register', [PageController::class, 'eventRegister'])->name('events.register');
    Route::get('/calendar', [PageController::class, 'eventCalendar'])->name('events.calendar');
    Route::get('/highlights', [PageController::class, 'eventHighlights'])->name('events.highlights');
});


/*
|--------------------------------------------------------------------------
| FAQS (FIXED - CLEAN VERSION)
|--------------------------------------------------------------------------
*/
Route::prefix('faqs')->group(function () {

    Route::get('/', [PageController::class, 'faqs'])->name('faqs.index');

    Route::get('/general', function () {
        return view('faqs.general');
    })->name('faqs.general');

    Route::get('/passport', function () {
        return view('faqs.passport');
    })->name('faqs.passport');

    Route::get('/consular', function () {
        return view('faqs.consular');
    })->name('faqs.consular');
});


/*
|--------------------------------------------------------------------------
| MESSAGES
|--------------------------------------------------------------------------
*/
Route::get('/message', [PageController::class, 'message'])->name('message');Route::get('/message', function () {
    return view('faqs.message');
})->name('message');