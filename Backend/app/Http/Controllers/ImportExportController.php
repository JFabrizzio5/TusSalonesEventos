<?php

namespace App\Http\Controllers;

use Illuminate\Database\Eloquent\ModelNotFoundException;
use App\Http\Requests\ImportExport\ImportRequest;
use App\Http\Requests\ImportExport\ExportRequest;
use App\Http\Requests\ImportExport\ExportReservRequest;
use App\Services\ImportExportService;
use App\Services\ImportExportReservService;
use App\Utils\ApiResponse;

class ImportExportController extends Controller
{
    use ApiResponse;

    public function __construct(protected ImportExportService $importExportService, protected ImportExportReservService $importExportReservationService) 
    {
    }
    
    /**
     * Importar CSV
     */
    public function importFromCSV(ImportRequest $request)
    {
        try{
            $filePath = $request->file('file')->getRealPath();
            $this->importExportService->importFromCSV($filePath);
            return $this->success(null,'Importación completada exitosamente');
        }catch(ModelNotFoundException $e){
            return $this->notFound();
        }
    }

    /**
     * Exportar CSV
     */
    public function exportToCSV(ExportRequest $request) 
    {
        try{
            $salonId = $request->salon_id;
            $directory = storage_path('app/exports');
            if (!file_exists($directory)) {
                mkdir($directory, 0777, true);
            }
            $filePath = $directory . "/salon_{$salonId}.csv";
            $this->importExportService->exportToCSV($salonId,$filePath);
            return response()->download($filePath)->deleteFileAfterSend(true);
        }catch(ModelNotFoundException $e){
            return $this->notFound();
        }
    }
    /**
     * Importar reservaciones
     */
    public function importReservations(ImportRequest $request)
    {
        try {
            $filePath = $request
                ->file('file')
                ->getRealPath();

            $this->importExportReservationService->importReservationsFromCSV(($filePath));
            return $this->success(null,'Reservaciones importadas correctamente');

        } catch (ModelNotFoundException $e) {
            return $this->notFound();
        }
    }

    /**
     * Exportar reservaciones
     */
    public function exportReservations(ExportReservRequest $request)
    {
        try {
            $eventId = $request->event_id;

            $directory = storage_path('app/exports');

            if (!file_exists($directory)) {
                mkdir($directory, 0777, true);
            }

            $filePath = $directory .
                "/reservations_event_{$eventId}.csv";
            $this->importExportReservationService->exportReservationsFromCSV($eventId,$filePath);
            return response()->download($filePath)->deleteFileAfterSend(true);
        } catch (ModelNotFoundException $e) {
            return $this->notFound();
        }
    }
}