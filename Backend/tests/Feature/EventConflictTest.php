<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EventConflictTest extends TestCase
{
    use RefreshDatabase;

    private EventType $eventType;

    protected function setUp(): void
    {
        parent::setUp();

        $this->eventType = EventType::query()->create([
            'name' => 'Cine',
            'slug' => 'cine',
            'is_active' => true,
        ]);
    }

    public function test_it_rejects_creating_an_event_contained_inside_an_existing_event(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 14:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'start_time' => '2026-06-01 11:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['start_time', 'end_time']);
    }

    public function test_it_rejects_creating_an_event_that_starts_before_and_ends_inside_existing_event(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 14:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'start_time' => '2026-06-01 09:00:00',
            'end_time' => '2026-06-01 11:00:00',
        ]));

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['start_time', 'end_time']);
    }

    public function test_it_rejects_creating_an_event_that_starts_inside_and_ends_after_existing_event(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 14:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'start_time' => '2026-06-01 13:00:00',
            'end_time' => '2026-06-01 15:00:00',
        ]));

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['start_time', 'end_time']);
    }

    public function test_it_allows_an_event_that_ends_exactly_when_another_starts(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'title' => 'Evento anterior',
            'start_time' => '2026-06-01 08:00:00',
            'end_time' => '2026-06-01 10:00:00',
        ]));

        $response->assertCreated()
            ->assertJsonPath('data.title', 'Evento anterior');
    }

    public function test_it_allows_an_event_that_starts_exactly_when_another_ends(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'title' => 'Evento posterior',
            'start_time' => '2026-06-01 12:00:00',
            'end_time' => '2026-06-01 14:00:00',
        ]));

        $response->assertCreated()
            ->assertJsonPath('data.title', 'Evento posterior');
    }

    public function test_it_allows_overlap_when_app_id_is_different(): void
    {
        Event::query()->create($this->eventPayload([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'app_id' => 'app-b',
            'userauth_id' => 'user-a',
            'start_time' => '2026-06-01 10:30:00',
            'end_time' => '2026-06-01 11:30:00',
        ]));

        $response->assertCreated()
            ->assertJsonPath('data.app_id', 'app-b');
    }

    public function test_it_allows_overlap_when_userauth_id_is_different(): void
    {
        Event::query()->create($this->eventPayload([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->postJson('/api/events', $this->eventPayload([
            'app_id' => 'app-a',
            'userauth_id' => 'user-b',
            'start_time' => '2026-06-01 10:30:00',
            'end_time' => '2026-06-01 11:30:00',
        ]));

        $response->assertCreated()
            ->assertJsonPath('data.userauth_id', 'user-b');
    }

    public function test_it_rejects_update_that_creates_a_conflict(): void
    {
        Event::query()->create($this->eventPayload([
            'title' => 'Evento existente',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $event = Event::query()->create($this->eventPayload([
            'title' => 'Evento a mover',
            'start_time' => '2026-06-01 14:00:00',
            'end_time' => '2026-06-01 16:00:00',
        ]));

        $response = $this->putJson("/api/events/{$event->id}", [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'start_time' => '2026-06-01 11:00:00',
            'end_time' => '2026-06-01 13:00:00',
        ]);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['start_time', 'end_time']);
    }

    public function test_it_allows_update_without_detecting_the_same_event_as_conflict(): void
    {
        $event = Event::query()->create($this->eventPayload([
            'title' => 'Evento existente',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->putJson("/api/events/{$event->id}", [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'title' => 'Evento actualizado',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]);

        $response->assertOk()
            ->assertJsonPath('data.title', 'Evento actualizado');
    }

    private function eventPayload(array $overrides = []): array
    {
        return array_merge([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $this->eventType->id,
            'title' => 'Evento conflicto',
            'description' => 'Evento de prueba',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ], $overrides);
    }
}
