<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class PageController extends Controller
{
    // Home & About
    public function home() { return view('frontend.home'); }
    public function about() { return view('frontend.about'); }
    public function contact() { return view('frontend.contacts'); }

    // Team & Ambassador
    public function teammembers() { return view('frontend.teammembers'); }
    public function ambassadorprofile() { return view('frontend.ambassadorprofile'); }
    public function deputyambassadorprofile() { return view('frontend.deputyambassadorprofile'); }

    // Visas & Travel
    public function visitus() { return view('frontend.visitus'); }
    public function visatypes() { return view('frontend.visatypes'); }
    public function visaservices() { return view('frontend.visaservices'); }
    public function visaissues() { return view('frontend.visaissues'); }
    public function visaFAQs() { return view('frontend.visaFAQs'); }
    public function planyourvisit() { return view('frontend.planyourvisit'); }
    public function travelDestinations() { return view('frontend.traveldestinations'); }
    public function traditionsandfestivals() { return view('frontend.traditionsandfestivals'); }
    public function supportingourpeople() { return view('frontend.supportingourpeople'); }
    public function studyinkenya() { return view('frontend.studyinkenya'); }

    // Services
    public function servicesqueries() { return view('frontend.servicesqueries'); }
    public function serviceshighlights() { return view('frontend.serviceshighlights'); }
    public function sendusamessage() { return view('frontend.sendusamessage'); }
    public function requestapassport() { return view('frontend.requestapassport'); }
    public function registerforevents() { return view('frontend.registerforevents'); }
    public function pressreleases() { return view('frontend.pressreleases'); }

    // Education & Scholarships
    public function scholarshipprograms() { return view('frontend.scholarshipprograms'); }
    public function applyforscholarship() { return view('frontend.applyforscholarship'); }
    public function studyinkenya2() { return view('frontend.studyinkenya'); }

    // FAQs & General Questions
    public function passportFAQs() { return view('frontend.passportFAQs'); }
    public function consularFAQs() { return view('frontend.consularFAQs'); }
    public function generalquestions() { return view('frontend.generalquestions'); }
    public function FAQs() { return view('frontend.FAQs'); }

    // Economy & Investment
    public function overviewoftheeconomy() { return view('frontend.overviewoftheeconomy'); }
    public function economictrends() { return view('frontend.economictrends'); }
    public function investmentopportunities() { return view('frontend.investmentopportunities'); }
    public function discoverkenya() { return view('frontend.discoverkenya'); }

    // Culture & Events
    public function ourvision() { return view('frontend.ourvision'); }
    public function ourmissionandvision() { return view('frontend.ourmissionandvision'); }
    public function ourmision() { return view('frontend.ourmision'); }
    public function ourlocation() { return view('frontend.ourlocation'); }
    public function ourhistory() { return view('frontend.ourhistory'); }
    public function openinghours() { return view('frontend.openinghours'); }
    public function missioninkorea() { return view('frontend.missioninkorea'); }
    public function kenyaswildlife() { return view('frontend.kenyaswildlife'); }
    public function howtoapplyforapassport() { return view('frontend.howtoapplyforapassport'); }
    public function eventhighlights() { return view('frontend.eventhighlights'); }
    public function eventcalender() { return view('frontend.eventcalender'); }
    public function embassyannouncements() { return view('frontend.embassyannouncements'); }
    public function culturalhighligts() { return view('frontend.culturalhighligts'); }
    public function calturegallery() { return view('frontend.calturegallery'); }
    public function assistanceforcitizens() { return view('frontend.assistanceforcitizens'); }
    public function applyforavisa() { return view('frontend.applyforavisa'); }
    public function aninspiringquote() { return view('frontend.aninspiringquote'); }
}