<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PageController;

// Home & basic pages
Route::get('/', [PageController::class, 'home'])->name('home');
Route::get('/about', [PageController::class, 'about'])->name('about');
Route::get('/contact', [PageController::class, 'contact'])->name('contact');

// Team & Ambassador
Route::get('/team-members', [PageController::class, 'teammembers'])->name('team.members');
Route::get('/ambassador-profile', [PageController::class, 'ambassadorprofile'])->name('ambassador.profile');
Route::get('/deputy-ambassador-profile', [PageController::class, 'deputyambassadorprofile'])->name('deputy.ambassador.profile');

// Visas & Travel
Route::get('/visit-us', [PageController::class, 'visitus'])->name('visit.us');
Route::get('/visa-types', [PageController::class, 'visatypes'])->name('visa.types');
Route::get('/visa-services', [PageController::class, 'visaservices'])->name('visa.services');
Route::get('/visa-issues', [PageController::class, 'visaissues'])->name('visa.issues');
Route::get('/visa-faqs', [PageController::class, 'visaFAQs'])->name('visa.faqs');
Route::get('/plan-your-visit', [PageController::class, 'planyourvisit'])->name('plan.visit');
Route::get('/travel-destinations', [PageController::class, 'travelDestinations'])->name('travel.destinations');
Route::get('/traditions-and-festivals', [PageController::class, 'traditionsandfestivals'])->name('traditions.festivals');
Route::get('/supporting-our-people', [PageController::class, 'supportingourpeople'])->name('supporting.people');
Route::get('/study-in-kenya', [PageController::class, 'studyinkenya'])->name('study.kenya');

// Services
Route::get('/services-queries', [PageController::class, 'servicesqueries'])->name('services.queries');
Route::get('/services-highlights', [PageController::class, 'serviceshighlights'])->name('services.highlights');
Route::get('/send-us-a-message', [PageController::class, 'sendusamessage'])->name('send.message');
Route::get('/request-a-passport', [PageController::class, 'requestapassport'])->name('request.passport');
Route::get('/register-for-events', [PageController::class, 'registerforevents'])->name('register.events');
Route::get('/press-releases', [PageController::class, 'pressreleases'])->name('press.releases');

// Education & Scholarships
Route::get('/scholarship-programs', [PageController::class, 'scholarshipprograms'])->name('scholarship.programs');
Route::get('/apply-for-scholarship', [PageController::class, 'applyforscholarship'])->name('apply.scholarship');

// FAQs & General Questions
Route::get('/passport-faqs', [PageController::class, 'passportFAQs'])->name('passport.faqs');
Route::get('/consular-faqs', [PageController::class, 'consularFAQs'])->name('consular.faqs');
Route::get('/general-questions', [PageController::class, 'generalquestions'])->name('general.questions');
Route::get('/faqs', [PageController::class, 'FAQs'])->name('faqs');

// Economy & Investment
Route::get('/overview-of-the-economy', [PageController::class, 'overviewoftheeconomy'])->name('overview.economy');
Route::get('/economic-trends', [PageController::class, 'economictrends'])->name('economic.trends');
Route::get('/investment-opportunities', [PageController::class, 'investmentopportunities'])->name('investment.opportunities');
Route::get('/discover-kenya', [PageController::class, 'discoverkenya'])->name('discover.kenya');

// Culture & Events
Route::get('/our-vision', [PageController::class, 'ourvision'])->name('our.vision');
Route::get('/our-mission-and-vision', [PageController::class, 'ourmissionandvision'])->name('our.mission.vision');
Route::get('/our-mision', [PageController::class, 'ourmision'])->name('our.mision');
Route::get('/our-location', [PageController::class, 'ourlocation'])->name('our.location');
Route::get('/our-history', [PageController::class, 'ourhistory'])->name('our.history');
Route::get('/opening-hours', [PageController::class, 'openinghours'])->name('opening.hours');
Route::get('/mission-in-korea', [PageController::class, 'missioninkorea'])->name('mission.korea');
Route::get('/kenyas-wildlife', [PageController::class, 'kenyaswildlife'])->name('kenya.wildlife');
Route::get('/how-to-apply-for-a-passport', [PageController::class, 'howtoapplyforapassport'])->name('apply.passport');

// Events & Announcements
Route::get('/event-highlights', [PageController::class, 'eventhighlights'])->name('event.highlights');
Route::get('/event-calendar', [PageController::class, 'eventcalender'])->name('event.calendar');
Route::get('/embassy-announcements', [PageController::class, 'embassyannouncements'])->name('embassy.announcements');

// Culture & Citizens
Route::get('/cultural-highlights', [PageController::class, 'culturalhighligts'])->name('cultural.highlights');
Route::get('/culture-gallery', [PageController::class, 'calturegallery'])->name('culture.gallery');
Route::get('/assistance-for-citizens', [PageController::class, 'assistanceforcitizens'])->name('assistance.citizens');
Route::get('/apply-for-a-visa', [PageController::class, 'applyforavisa'])->name('apply.visa');
Route::get('/an-inspiring-quote', [PageController::class, 'aninspiringquote'])->name('inspiring.quote');