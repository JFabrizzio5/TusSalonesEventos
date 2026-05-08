<?php

use App\Http\Controllers\CalendarController;
use App\Http\Controllers\EventController;
use App\Http\Controllers\EventImportExportController;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Route;
use Sentry\Breadcrumb;
use Sentry\SentrySdk;
use Sentry\State\Scope;

// --- CometaX Default Tools ---
Route::get('/health', function () {
    return response()->json(['status' => 'ok', 'app' => env('APP_NAME')]);
});

// --- Rutas de Eventos ---
Route::get('events', [EventController::class, 'index'])->name('events.index');
Route::post('events/import', [EventImportExportController::class, 'import'])->name('events.import');
Route::get('events/export', [EventImportExportController::class, 'export'])->name('events.export');
Route::post('events', [EventController::class, 'store'])->name('events.store');
Route::get('events/{event}', [EventController::class, 'show'])->name('events.show');
Route::put('events/{event}', [EventController::class, 'update'])->name('events.update');
Route::delete('events/{event}', [EventController::class, 'destroy'])->name('events.destroy');

// --- Rutas de Calendario ---
Route::get('calendar/week', [CalendarController::class, 'week'])->name('calendar.week');
Route::get('calendar/month', [CalendarController::class, 'month'])->name('calendar.month');

// --- Diagnóstico Sentry Full-Stack (CometaX Diagnostics) ---
Route::get('/test-sentry', function () {
    // 0. Forzar nombre de transacción para Discover y Metrics
    SentrySdk::getCurrentHub()->getTransaction()?->setName('cometax.diagnostic.full_suite');

    // 1. Identidad de Usuario (Aparecerá en Discover > User)
    \Sentry\configureScope(function (Scope $scope): void {
        $scope->setUser(['id' => 777, 'email' => 'TusSalonesEventos-diagnostic@cometax.com', 'username' => 'TusSalonesEventosMaster']);
        $scope->setTag('cometax_diagnostic', 'true');
    });

    // 2. Métrica de inicio de diagnóstico
    \Sentry\traceMetrics()->count('cometax.diagnostic.start', 1);

    // 3. Breadcrumb: Paso previo a DB
    \Sentry\addBreadcrumb(new Breadcrumb(Breadcrumb::LEVEL_INFO, Breadcrumb::TYPE_DEFAULT, 'db', 'Intentando conectar a DB para validar drivers...'));

    // 4. Trace de Conexión a Base de Datos (Esto capturará errores de Driver)
    try {
        DB::connection()->getPdo();
        \Sentry\addBreadcrumb(new Breadcrumb(Breadcrumb::LEVEL_INFO, Breadcrumb::TYPE_DEFAULT, 'db', 'Conexión a DB exitosa.'));
    } catch (Exception $e) {
        Log::error('Fallo de conectividad detectado en TusSalonesEventos: '.$e->getMessage());
    }

    // 5. El Gran Final con Excepción Completa
    \Sentry\flush(); // <--- CRÍTICO: Asegura que las métricas y logs se envíen antes de que Laravel mate el proceso
    throw new Exception('🔥 Diagnóstico Discover en TusSalonesEventos: Si ves esto, cambia el filtro de proyecto en Sentry a "All Projects".');
});
