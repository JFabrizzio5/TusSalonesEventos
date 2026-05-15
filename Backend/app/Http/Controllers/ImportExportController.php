<?php

namespace App\Http\Controllers;

use Illuminate\Database\Eloquent\ModelNotFoundException;
use App\Http\Requests\ImportExport\ImportRequest;
use App\Http\Requests\ImportExport\ExportRequest;
use App\Services\ImportExportService;
use App\Utils\ApiResponse;

class ImportExportController extends Controller
{
    use ApiResponse;

    public function __construct(protected ImportExportService $importExportService) 
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
}