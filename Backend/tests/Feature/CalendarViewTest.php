<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CalendarViewTest extends TestCase
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

    public function test_weekly_calendar_returns_only_events_for_tenant_and_range(): void
    {
        $included = Event::query()->create($this->eventPayload([
            'title' => 'Evento semanal',
            'start_time' => '2026-06-03 10:00:00',
            'end_time' => '2026-06-03 12:00:00',
        ]));

        Event::query()->create($this->eventPayload([
            'title' => 'Evento fuera de semana',
            'start_time' => '2026-06-10 10:00:00',
            'end_time' => '2026-06-10 12:00:00',
        ]));

        Event::query()->create($this->eventPayload([
            'app_id' => 'app-b',
            'userauth_id' => 'user-b',
            'title' => 'Evento externo',
            'start_time' => '2026-06-03 10:00:00',
            'end_time' => '2026-06-03 12:00:00',
        ]));

        $response = $this->getJson('/api/calendar/week?app_id=app-a&userauth_id=user-a&week_start=2026-06-01');

        $response->assertOk()
            ->assertJsonPath('data.view', 'week')
            ->assertJsonCount(1, 'data.events')
            ->assertJsonPath('data.events.0.id', $included->id)
            ->assertJsonPath('data.events.0.title', 'Evento semanal');
    }

    public function test_weekly_calendar_includes_events_that_overlap_the_range(): void
    {
        $included = Event::query()->create($this->eventPayload([
            'title' => 'Evento cruzado',
            'start_time' => '2026-05-31 22:00:00',
            'end_time' => '2026-06-01 02:00:00',
        ]));

        $response = $this->getJson('/api/calendar/week?app_id=app-a&userauth_id=user-a&week_start=2026-06-01');

        $response->assertOk()
            ->assertJsonCount(1, 'data.events')
            ->assertJsonPath('data.events.0.id', $included->id);
    }

    public function test_monthly_calendar_returns_only_events_for_tenant_and_month(): void
    {
        $included = Event::query()->create($this->eventPayload([
            'title' => 'Evento mensual',
            'start_time' => '2026-07-15 18:00:00',
            'end_time' => '2026-07-15 20:00:00',
        ]));

        Event::query()->create($this->eventPayload([
            'title' => 'Evento fuera de mes',
            'start_time' => '2026-08-01 10:00:00',
            'end_time' => '2026-08-01 12:00:00',
        ]));

        Event::query()->create($this->eventPayload([
            'app_id' => 'app-b',
            'userauth_id' => 'user-b',
            'title' => 'Evento externo mensual',
            'start_time' => '2026-07-15 18:00:00',
            'end_time' => '2026-07-15 20:00:00',
        ]));

        $response = $this->getJson('/api/calendar/month?app_id=app-a&userauth_id=user-a&year=2026&month=7');

        $response->assertOk()
            ->assertJsonPath('data.view', 'month')
            ->assertJsonCount(1, 'data.events')
            ->assertJsonPath('data.events.0.id', $included->id)
            ->assertJsonPath('data.events.0.title', 'Evento mensual');
    }

    public function test_calendar_validates_required_parameters(): void
    {
        $this->getJson('/api/calendar/week')
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['app_id', 'userauth_id', 'week_start']);

        $this->getJson('/api/calendar/month?app_id=app-a&userauth_id=user-a&year=2026&month=13')
            ->assertUnprocessable()
            ->assertJsonValidationErrors(['month']);
    }

    private function eventPayload(array $overrides = []): array
    {
        return array_merge([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $this->eventType->id,
            'title' => 'Evento calendario',
            'description' => 'Evento de prueba',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ], $overrides);
    }
}
