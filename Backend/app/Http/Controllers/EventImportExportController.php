<?php

namespace App\Http\Controllers;

use App\Http\Requests\ExportEventsRequest;
use App\Http\Requests\ImportEventsRequest;
use App\Services\EventImportExportService;
use Illuminate\Http\JsonResponse;
use Symfony\Component\HttpFoundation\StreamedResponse;

class EventImportExportController extends Controller
{
    public function __construct(private readonly EventImportExportService $importExport) {}

    // --- IMPORT_EVENTS ---
    // Descripción: Importa eventos desde archivo CSV o ICS con rechazo parcial.
    // Parámetros: app_id, userauth_id, format, file
    // Respuesta: JSON Structure
    // -----------------------------
    public function import(ImportEventsRequest $request): JsonResponse
    {
        $validated = $request->validated();

        return response()->json($this->importExport->import(
            $validated['app_id'],
            $validated['userauth_id'],
            $validated['format'],
            $request->file('file')->getRealPath(),
        ));
    }

    // --- EXPORT_EVENTS ---
    // Descripción: Exporta eventos filtrados a CSV o ICS.
    // Parámetros: app_id, userauth_id, format, start_time, end_time, event_type_id, event_type_slug
    // Respuesta: JSON Structure
    // -----------------------------
    public function export(ExportEventsRequest $request): StreamedResponse
    {
        $validated = $request->validated();

        return $this->importExport->export($validated);
    }
}
