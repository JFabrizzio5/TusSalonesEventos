<?php

namespace App\Http\Controllers;

use App\Http\Resources\EventResource;
use App\Services\EventService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CalendarController extends Controller
{
    public function __construct(private readonly EventService $events) {}

    // --- WEEKLY_CALENDAR ---
    // Descripción: Devuelve eventos para vista semanal aislados por app_id y userauth_id.
    // Parámetros: app_id, userauth_id, week_start
    // Respuesta: JSON Structure
    // -----------------------------
    public function week(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
            'week_start' => ['required', 'date'],
        ]);

        $calendar = $this->events->weeklyCalendar(
            $validated['app_id'],
            $validated['userauth_id'],
            $validated['week_start'],
        );

        return $this->calendarResponse($request, $calendar);
    }

    // --- MONTHLY_CALENDAR ---
    // Descripción: Devuelve eventos para vista mensual aislados por app_id y userauth_id.
    // Parámetros: app_id, userauth_id, year, month
    // Respuesta: JSON Structure
    // -----------------------------
    public function month(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
            'year' => ['required', 'integer', 'min:1900', 'max:2200'],
            'month' => ['required', 'integer', 'between:1,12'],
        ]);

        $calendar = $this->events->monthlyCalendar(
            $validated['app_id'],
            $validated['userauth_id'],
            (int) $validated['year'],
            (int) $validated['month'],
        );

        return $this->calendarResponse($request, $calendar);
    }

    private function calendarResponse(Request $request, array $calendar): JsonResponse
    {
        return response()->json([
            'data' => [
                'view' => $calendar['view'],
                'range_start' => $calendar['range_start']->toISOString(),
                'range_end' => $calendar['range_end']->toISOString(),
                'events' => EventResource::collection($calendar['events'])->resolve($request),
            ],
        ]);
    }
}
