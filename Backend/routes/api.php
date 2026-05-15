<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\SalonController;
use App\Http\Controllers\ZoneController;
use App\Http\Controllers\SeatMapController;
use App\Http\Controllers\SeatController;
use App\Http\Controllers\TicketController;
use App\Http\Controllers\ImportExportController;


// --- CometaX Default Tools ---
Route::get('/health', function () {
    return response()->json(['status' => 'ok', 'app' => env('APP_NAME')]);
});


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

// --- Rutas de API ---
Route::apiResource('salons', SalonController::class);
Route::get('salons/{id}/capacity', [SalonController::class, 'capacity']);
Route::get('salons/{id}/seat-map', [SeatMapController::class, 'show']);
Route::apiResource('zones', ZoneController::class);
Route::post('seats', [SeatController::class, 'store']);
Route::put('seats/{id}', [SeatController::class, 'update']);
Route::patch('seats/{id}/status', [SeatController::class, 'updateStatus']);
Route::apiResource('tickets', TicketController::class);
Route::prefix('import-export')->group(function () {

    Route::post(
        '/import/seats',
        [ImportExportController::class, 'importFromCSV']
    );

    Route::get(
        '/export/seats',
        [ImportExportController::class, 'exportToCSV']
    );
});