<?php

namespace App\Repositories;

use App\Models\Event;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Collection;

class EventRepository
{
    public function paginateForTenant(string $appId, string $userauthId, array $filters = []): LengthAwarePaginator
    {
        return $this->filteredQueryForTenant($appId, $userauthId, $filters)
            ->paginate($filters['per_page'] ?? 15);
    }

    public function getFilteredForTenant(string $appId, string $userauthId, array $filters = []): Collection
    {
        return $this->filteredQueryForTenant($appId, $userauthId, $filters)->get();
    }

    private function filteredQueryForTenant(string $appId, string $userauthId, array $filters = []): Builder
    {
        return Event::query()
            ->with('eventType')
            ->forTenant($appId, $userauthId)
            ->when($filters['event_type_id'] ?? null, fn ($query, $eventTypeId) => $query->where('event_type_id', $eventTypeId))
            ->when($filters['event_type_slug'] ?? null, fn ($query, $eventTypeSlug) => $query->whereHas('eventType', fn ($eventTypeQuery) => $eventTypeQuery->where('slug', $eventTypeSlug)))
            ->when($filters['start_time'] ?? null, fn ($query, $startTime) => $query->where('end_time', '>=', $startTime))
            ->when($filters['end_time'] ?? null, fn ($query, $endTime) => $query->where('start_time', '<=', $endTime))
            ->orderBy('start_time');
    }

    public function findForTenant(int $eventId, string $appId, string $userauthId): ?Event
    {
        return Event::query()
            ->with('eventType')
            ->forTenant($appId, $userauthId)
            ->whereKey($eventId)
            ->first();
    }

    public function rangeForTenant(string $appId, string $userauthId, mixed $rangeStart, mixed $rangeEnd): Collection
    {
        return Event::query()
            ->with('eventType')
            ->forTenant($appId, $userauthId)
            ->where('start_time', '<=', $rangeEnd)
            ->where('end_time', '>=', $rangeStart)
            ->orderBy('start_time')
            ->get();
    }

    public function hasScheduleOverlap(string $appId, string $userauthId, mixed $startTime, mixed $endTime, ?int $ignoreEventId = null): bool
    {
        return Event::query()
            ->forTenant($appId, $userauthId)
            ->where('start_time', '<', $endTime)
            ->where('end_time', '>', $startTime)
            ->when($ignoreEventId !== null, fn ($query) => $query->whereKeyNot($ignoreEventId))
            ->exists();
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

    public function deleteForTenant(string $appId, string $userauthId): int
    {
        return Event::query()
            ->forTenant($appId, $userauthId)
            ->delete();
    }
}
