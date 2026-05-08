<?php

namespace App\Services;

use App\Models\Event;
use App\Repositories\EventRepository;
use Carbon\CarbonImmutable;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Arr;
use Illuminate\Validation\ValidationException;

class EventService
{
    public function __construct(private readonly EventRepository $events) {}

    public function list(array $filters): LengthAwarePaginator
    {
        return $this->events->paginateForTenant(
            $filters['app_id'],
            $filters['userauth_id'],
            $filters,
        );
    }

    public function get(int $eventId, string $appId, string $userauthId): Event
    {
        $event = $this->events->findForTenant($eventId, $appId, $userauthId);

        abort_if($event === null, 404, 'Event not found for the provided tenant.');

        return $event;
    }

    public function create(array $data): Event
    {
        $this->ensureValidTimeRange($data['start_time'], $data['end_time']);
        $this->ensureNoScheduleConflict($data['app_id'], $data['userauth_id'], $data['start_time'], $data['end_time']);

        return $this->events->create($data);
    }

    public function update(int $eventId, array $data): Event
    {
        $event = $this->get($eventId, $data['app_id'], $data['userauth_id']);
        $updateData = Arr::except($data, ['app_id', 'userauth_id']);
        $startTime = $updateData['start_time'] ?? $event->start_time;
        $endTime = $updateData['end_time'] ?? $event->end_time;

        $this->ensureValidTimeRange($startTime, $endTime);
        $this->ensureNoScheduleConflict($event->app_id, $event->userauth_id, $startTime, $endTime, $event->id);

        return $this->events->update($event, $updateData);
    }

    public function delete(int $eventId, string $appId, string $userauthId): void
    {
        $event = $this->get($eventId, $appId, $userauthId);

        $this->events->delete($event);
    }

    public function weeklyCalendar(string $appId, string $userauthId, string $weekStart): array
    {
        $rangeStart = CarbonImmutable::parse($weekStart)->startOfDay();
        $rangeEnd = $rangeStart->addDays(7)->subSecond();

        return [
            'view' => 'week',
            'range_start' => $rangeStart,
            'range_end' => $rangeEnd,
            'events' => $this->events->rangeForTenant($appId, $userauthId, $rangeStart, $rangeEnd),
        ];
    }

    public function monthlyCalendar(string $appId, string $userauthId, int $year, int $month): array
    {
        $rangeStart = CarbonImmutable::create($year, $month, 1)->startOfDay();
        $rangeEnd = $rangeStart->endOfMonth();

        return [
            'view' => 'month',
            'range_start' => $rangeStart,
            'range_end' => $rangeEnd,
            'events' => $this->events->rangeForTenant($appId, $userauthId, $rangeStart, $rangeEnd),
        ];
    }

    private function ensureValidTimeRange(mixed $startTime, mixed $endTime): void
    {
        if (strtotime((string) $endTime) <= strtotime((string) $startTime)) {
            throw ValidationException::withMessages([
                'end_time' => ['La hora de finalización debe ser posterior a la hora de inicio.'],
            ]);
        }
    }

    private function ensureNoScheduleConflict(string $appId, string $userauthId, mixed $startTime, mixed $endTime, ?int $ignoreEventId = null): void
    {
        if (! $this->events->hasScheduleOverlap($appId, $userauthId, $startTime, $endTime, $ignoreEventId)) {
            return;
        }

        throw ValidationException::withMessages([
            'start_time' => ['El horario se traslapa con otro evento existente.'],
            'end_time' => ['El horario se traslapa con otro evento existente.'],
        ]);
    }
}
