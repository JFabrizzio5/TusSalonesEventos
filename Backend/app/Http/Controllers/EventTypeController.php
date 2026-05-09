<?php

namespace App\Http\Controllers;

use App\Http\Resources\EventTypeResource;
use App\Models\EventType;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class EventTypeController extends Controller
{
    // --- LIST_EVENT_TYPES ---
    // Descripción: Lista tipos de evento activos para formularios, filtros y selectores dinámicos.
    // Parámetros: Ninguno
    // Respuesta: JSON Structure
    // -----------------------------
    public function index(): AnonymousResourceCollection
    {
        return EventTypeResource::collection(
            EventType::query()
                ->where('is_active', true)
                ->orderBy('name')
                ->get()
        );
    }
}
