<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class PageController extends Controller
{
    // ================= MAIN =================
    public function home() { return view('pages.home'); }
    public function about() { return view('pages.about'); }
    public function contact() { return view('pages.contacts'); }
    public function visitus() { return view('pages.visitus'); }
    public function message() { return view('pages.sendusamessage'); }


    // ================= EMBASSY =================
    public function ambassador() { return view('embassy.ambassadorprofile'); }
    public function embassyHistory() { return view('embassy.ourhistory'); }


    // ================= VISA =================
    public function visatypes() { return view('services.visatypes'); }
    public function visaservices() { return view('visa.services'); }
    public function visaissues() { return view('services.visa.issues'); }
    public function faqs() { return view('services.visa.faqs'); }


    // ================= KENYA =================
    public function discover() { return view('discover.index'); }


    // ================= COMMUNITY =================
    public function communityIndex() { return view('community.index'); }
    public function communityHistory() { return view('community.history'); }
    public function location() { return view('community.location'); }
    public function hours() { return view('community.hours'); }
    public function mission() { return view('community.mission'); }
    public function vision() { return view('community.vision'); }


    // ================= SERVICES =================
    public function passportRequest() { return view('services.passport.request'); }
    public function passportApply() { return view('services.passport.apply'); }
    public function queries() { return view('services.queries'); }
    public function highlights() { return view('services.highlights'); }


    // ================= EVENTS =================
    public function events() { return view('events.index'); }
    public function eventRegister() { return view('events.register'); }
    public function eventCalendar() { return view('events.calendar'); }
    public function eventHighlights() { return view('events.highlights'); }
}