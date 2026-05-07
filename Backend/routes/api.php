<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\EventController;

// --- CometaX Default Tools ---
Route::get('/health', function () {
    return response()->json(['status' => 'ok', 'app' => env('APP_NAME')]);
});

// --- Diagnóstico Sentry Full-Stack (CometaX Diagnostics) ---
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

 // --- Rutas de Eventos ---
Route::apiResource('events', EventController::class)->only(['index', 'show', 'store', 'update', 'destroy']);

Route::get('events', [EventController::class, 'index'])->name('events.index');
Route::post('events', [EventController::class, 'store'])->name('events.store');
Route::get('events/{event}', [EventController::class, 'show'])->name('events.show');
Route::put('events/{event}', [EventController::class, 'update'])->name('events.update');
Route::delete('events/{event}', [EventController::class, 'destroy'])->name('events.destroy');

Route::get('/test-sentry', function () {
    // 0. Forzar nombre de transacción para Discover y Metrics
    \Sentry\SentrySdk::getCurrentHub()->getTransaction()?->setName('cometax.diagnostic.full_suite');

    // 1. Identidad de Usuario (Aparecerá en Discover > User)
    \Sentry\configureScope(function (\Sentry\State\Scope $scope): void {
        $scope->setUser(['id' => 777, 'email' => 'TusSalonesEventos-diagnostic@cometax.com', 'username' => 'TusSalonesEventosMaster']);
        $scope->setTag('cometax_diagnostic', 'true');
    });

    // 2. Métrica de inicio de diagnóstico
    \Sentry\traceMetrics()->count('cometax.diagnostic.start', 1);

    // 3. Breadcrumb: Paso previo a DB
    \Sentry\addBreadcrumb(new \Sentry\Breadcrumb(\Sentry\Breadcrumb::LEVEL_INFO, \Sentry\Breadcrumb::TYPE_DEFAULT, 'db', 'Intentando conectar a DB para validar drivers...'));

    // 4. Trace de Conexión a Base de Datos (Esto capturará errores de Driver)
    try {
        \Illuminate\Support\Facades\DB::connection()->getPdo();
        \Sentry\addBreadcrumb(new \Sentry\Breadcrumb(\Sentry\Breadcrumb::LEVEL_INFO, \Sentry\Breadcrumb::TYPE_DEFAULT, 'db', 'Conexión a DB exitosa.'));
    } catch (\Exception $e) {
        \Illuminate\Support\Facades\Log::error('Fallo de conectividad detectado en TusSalonesEventos: ' . $e->getMessage());
    }

    // 5. El Gran Final con Excepción Completa
    \Sentry\flush(); // <--- CRÍTICO: Asegura que las métricas y logs se envíen antes de que Laravel mate el proceso
    throw new \Exception('🔥 Diagnóstico Discover en TusSalonesEventos: Si ves esto, cambia el filtro de proyecto en Sentry a "All Projects".');
});
