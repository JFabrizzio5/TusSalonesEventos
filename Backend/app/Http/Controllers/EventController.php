<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreEventRequest;
use App\Http\Requests\UpdateEventRequest;
use App\Http\Resources\EventResource;
use App\Services\EventService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use Illuminate\Http\Response;

class EventController extends Controller
{
    public function __construct(private readonly EventService $events) {}

    // --- LIST_EVENTS ---
    // Descripción: Lista eventos filtrados por app_id, userauth_id, fecha y tipo de evento.
    // Parámetros: app_id, userauth_id, start_time, end_time, event_type_id, event_type_slug, per_page
    // Respuesta: JSON Structure
    // -----------------------------
    public function index(Request $request): AnonymousResourceCollection
    {
        $filters = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
            'event_type_id' => ['sometimes', 'integer', 'exists:event_types,id'],
            'event_type_slug' => ['sometimes', 'string', 'max:255', 'exists:event_types,slug'],
            'start_time' => ['sometimes', 'date'],
            'end_time' => ['sometimes', 'date'],
            'per_page' => ['sometimes', 'integer', 'min:1', 'max:100'],
        ]);

        return EventResource::collection($this->events->list($filters));
    }

    // --- SHOW_EVENT ---
    // Descripción: Obtiene el detalle de un evento aislado por app_id y userauth_id.
    // Parámetros: app_id, userauth_id, event
    // Respuesta: JSON Structure
    // -----------------------------
    public function show(Request $request, int $event): EventResource
    {
        $tenant = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
        ]);

        return EventResource::make($this->events->get($event, $tenant['app_id'], $tenant['userauth_id']));
    }

    // --- CREATE_EVENT ---
    // Descripción: Crea un evento validando app_id, userauth_id y datos requeridos.
    // Parámetros: app_id, userauth_id, event_type_id, title, description, start_time, end_time
    // Respuesta: JSON Structure
    // -----------------------------
    public function store(StoreEventRequest $request): JsonResponse
    {
        $event = $this->events->create($request->validated());

        return EventResource::make($event)
            ->response()
            ->setStatusCode(Response::HTTP_CREATED);
    }

    // --- UPDATE_EVENT ---
    // Descripción: Actualiza un evento existente aislado por app_id y userauth_id.
    // Parámetros: app_id, userauth_id, event, event_type_id, title, description, start_time, end_time
    // Respuesta: JSON Structure
    // -----------------------------
    public function update(UpdateEventRequest $request, int $event): EventResource
    {
        return EventResource::make($this->events->update($event, $request->validated()));
    }

    // --- DELETE_EVENT ---
    // Descripción: Elimina un evento aislado por app_id y userauth_id.
    // Parámetros: app_id, userauth_id, event
    // Respuesta: JSON Structure
    // -----------------------------
    public function destroy(Request $request, int $event): JsonResponse
    {
        $tenant = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
        ]);

        $this->events->delete($event, $tenant['app_id'], $tenant['userauth_id']);

        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    public function reset(Request $request): JsonResponse
    {
        $tenant = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
        ]);

        $deleted = $this->events->deleteByTenant($tenant['app_id'], $tenant['userauth_id']);

        return response()->json([
            'message' => 'Eventos eliminados',
            'deleted_count' => $deleted,
        ]);
    }
}
