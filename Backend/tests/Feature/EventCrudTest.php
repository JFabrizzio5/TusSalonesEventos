<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EventCrudTest extends TestCase
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

    public function test_it_creates_an_event_with_tenant_fields(): void
    {
        $response = $this->postJson('/api/events', $this->eventPayload());

        $response->assertCreated()
            ->assertJsonPath('data.app_id', 'app-a')
            ->assertJsonPath('data.userauth_id', 'user-a')
            ->assertJsonPath('data.title', 'Evento principal');

        $this->assertDatabaseHas('events', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'title' => 'Evento principal',
        ]);
    }

    public function test_it_lists_only_events_for_the_requested_tenant(): void
    {
        $ownEvent = Event::query()->create($this->eventPayload());
        Event::query()->create($this->eventPayload([
            'app_id' => 'app-b',
            'userauth_id' => 'user-b',
            'title' => 'Evento externo',
        ]));

        $response = $this->getJson('/api/events?app_id=app-a&userauth_id=user-a');

        $response->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $ownEvent->id)
            ->assertJsonPath('data.0.title', 'Evento principal');
    }

    public function test_it_shows_an_event_only_for_the_requested_tenant(): void
    {
        $event = Event::query()->create($this->eventPayload());

        $this->getJson("/api/events/{$event->id}?app_id=app-a&userauth_id=user-a")
            ->assertOk()
            ->assertJsonPath('data.id', $event->id);

        $this->getJson("/api/events/{$event->id}?app_id=app-b&userauth_id=user-b")
            ->assertNotFound();
    }

    public function test_it_updates_an_event_for_the_requested_tenant(): void
    {
        $event = Event::query()->create($this->eventPayload());

        $response = $this->putJson("/api/events/{$event->id}", [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'title' => 'Evento actualizado',
        ]);

        $response->assertOk()
            ->assertJsonPath('data.title', 'Evento actualizado');

        $this->assertDatabaseHas('events', [
            'id' => $event->id,
            'title' => 'Evento actualizado',
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
        ]);
    }

    public function test_it_deletes_an_event_for_the_requested_tenant(): void
    {
        $event = Event::query()->create($this->eventPayload());

        $this->deleteJson("/api/events/{$event->id}?app_id=app-a&userauth_id=user-a")
            ->assertNoContent();

        $this->assertDatabaseMissing('events', [
            'id' => $event->id,
        ]);
    }

    private function eventPayload(array $overrides = []): array
    {
        return array_merge([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $this->eventType->id,
            'title' => 'Evento principal',
            'description' => 'Evento de prueba',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ], $overrides);
    }
}
