<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EventFilterTest extends TestCase
{
    use RefreshDatabase;

    private EventType $cineType;

    private EventType $torneoType;

    protected function setUp(): void
    {
        parent::setUp();

        $this->cineType = EventType::query()->create([
            'name' => 'Cine',
            'slug' => 'cine',
            'is_active' => true,
        ]);

        $this->torneoType = EventType::query()->create([
            'name' => 'Torneo',
            'slug' => 'torneo',
            'is_active' => true,
        ]);
    }

    public function test_filters_require_app_id_and_userauth_id(): void
    {
        $this->getJson('/api/events')
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['app_id', 'userauth_id']);
    }

    public function test_filters_by_app_id_and_userauth_id(): void
    {
        $ownEvent = Event::query()->create($this->eventPayload([
            'title' => 'Evento propio',
        ]));

        Event::query()->create($this->eventPayload([
            'app_id' => 'app-b',
            'title' => 'Evento de otra app',
        ]));

        Event::query()->create($this->eventPayload([
            'userauth_id' => 'user-b',
            'title' => 'Evento de otro usuario',
        ]));

        $response = $this->getJson('/api/events?app_id=app-a&userauth_id=user-a');

        $response->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $ownEvent->id)
            ->assertJsonPath('data.0.title', 'Evento propio');
    }

    public function test_filters_by_date_range_and_includes_overlapping_events(): void
    {
        $inside = Event::query()->create($this->eventPayload([
            'title' => 'Dentro del rango',
            'start_time' => '2026-06-05 10:00:00',
            'end_time' => '2026-06-05 12:00:00',
        ]));

        $overlapping = Event::query()->create($this->eventPayload([
            'title' => 'Cruza el rango',
            'start_time' => '2026-05-31 22:00:00',
            'end_time' => '2026-06-01 02:00:00',
        ]));

        Event::query()->create($this->eventPayload([
            'title' => 'Fuera del rango',
            'start_time' => '2026-06-10 10:00:00',
            'end_time' => '2026-06-10 12:00:00',
        ]));

        $response = $this->getJson('/api/events?app_id=app-a&userauth_id=user-a&start_time=2026-06-01&end_time=2026-06-07');

        $response->assertOk()
            ->assertJsonCount(2, 'data')
            ->assertJsonPath('data.0.id', $overlapping->id)
            ->assertJsonPath('data.1.id', $inside->id);
    }

    public function test_filters_by_event_type_id(): void
    {
        $cineEvent = Event::query()->create($this->eventPayload([
            'title' => 'Evento cine',
            'event_type_id' => $this->cineType->id,
        ]));

        Event::query()->create($this->eventPayload([
            'title' => 'Evento torneo',
            'event_type_id' => $this->torneoType->id,
        ]));

        $response = $this->getJson("/api/events?app_id=app-a&userauth_id=user-a&event_type_id={$this->cineType->id}");

        $response->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $cineEvent->id)
            ->assertJsonPath('data.0.event_type.slug', 'cine');
    }

    public function test_filters_by_event_type_slug(): void
    {
        $torneoEvent = Event::query()->create($this->eventPayload([
            'title' => 'Evento torneo',
            'event_type_id' => $this->torneoType->id,
        ]));

        Event::query()->create($this->eventPayload([
            'title' => 'Evento cine',
            'event_type_id' => $this->cineType->id,
        ]));

        $response = $this->getJson('/api/events?app_id=app-a&userauth_id=user-a&event_type_slug=torneo');

        $response->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $torneoEvent->id)
            ->assertJsonPath('data.0.event_type.slug', 'torneo');
    }

    public function test_filters_respect_per_page(): void
    {
        Event::query()->create($this->eventPayload(['title' => 'Evento 1']));
        Event::query()->create($this->eventPayload(['title' => 'Evento 2']));
        Event::query()->create($this->eventPayload(['title' => 'Evento 3']));

        $response = $this->getJson('/api/events?app_id=app-a&userauth_id=user-a&per_page=2');

        $response->assertOk()
            ->assertJsonCount(2, 'data')
            ->assertJsonPath('meta.per_page', 2)
            ->assertJsonPath('meta.total', 3);
    }

    private function eventPayload(array $overrides = []): array
    {
        return array_merge([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $this->cineType->id,
            'title' => 'Evento filtrado',
            'description' => 'Evento de prueba',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ], $overrides);
    }
}
