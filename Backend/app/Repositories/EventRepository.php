<?php

namespace App\Repositories;

use App\Models\Event;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

class EventRepository
{
    public function paginateForTenant(string $appId, string $userauthId, array $filters = []): LengthAwarePaginator
    {
        return Event::query()
            ->with('eventType')
            ->forTenant($appId, $userauthId)
            ->when($filters['event_type_id'] ?? null, fn ($query, $eventTypeId) => $query->where('event_type_id', $eventTypeId))
            ->when($filters['start_time'] ?? null, fn ($query, $startTime) => $query->where('end_time', '>=', $startTime))
            ->when($filters['end_time'] ?? null, fn ($query, $endTime) => $query->where('start_time', '<=', $endTime))
            ->orderBy('start_time')
            ->paginate($filters['per_page'] ?? 15);
    }

    public function findForTenant(int $eventId, string $appId, string $userauthId): ?Event
    {
        return Event::query()
            ->with('eventType')
            ->forTenant($appId, $userauthId)
            ->whereKey($eventId)
            ->first();
    }

    public function create(array $data): Event
    {
        return Event::query()->create($data)->load('eventType');
    }

    public function update(Event $event, array $data): Event
    {
        $event->update($data);

        return $event->refresh()->load('eventType');
    }

    public function delete(Event $event): void
    {
        $event->delete();
    }
}