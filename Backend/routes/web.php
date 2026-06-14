<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/calendar', function (){
    return view('calendar');
})->name('calendar');

Route::get('/events-management', function(){
    return view('event');
})->name('events-management');