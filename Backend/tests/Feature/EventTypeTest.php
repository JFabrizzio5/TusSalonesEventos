<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EventTypeTest extends TestCase
{
    use RefreshDatabase;

    public function test_it_lists_only_active_event_types(): void
    {
        $cine = EventType::query()->create([
            'name' => 'Cine',
            'slug' => 'cine',
            'is_active' => true,
        ]);

        EventType::query()->create([
            'name' => 'Tipo inactivo',
            'slug' => 'tipo-inactivo',
            'is_active' => false,
        ]);

        $response = $this->getJson('/api/event-types');

        $response->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.id', $cine->id)
            ->assertJsonPath('data.0.name', 'Cine')
            ->assertJsonPath('data.0.slug', 'cine')
            ->assertJsonPath('data.0.is_active', true);
    }

    public function test_events_can_be_created_with_dynamic_event_type_and_metadata(): void
    {
        $eventType = EventType::query()->create([
            'name' => 'Llamada de Zoom',
            'slug' => 'llamada-de-zoom',
            'is_active' => true,
        ]);

        $response = $this->postJson('/api/events', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $eventType->id,
            'title' => 'Planeacion remota',
            'description' => 'Sesion de trabajo',
            'metadata' => [
                'meeting_url' => 'https://zoom.example/test',
                'host' => 'Javier',
            ],
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]);

        $response->assertCreated()
            ->assertJsonPath('data.event_type.slug', 'llamada-de-zoom')
            ->assertJsonPath('data.metadata.meeting_url', 'https://zoom.example/test')
            ->assertJsonPath('data.metadata.host', 'Javier');

        $this->assertDatabaseHas('events', [
            'title' => 'Planeacion remota',
            'event_type_id' => $eventType->id,
        ]);
    }

    public function test_event_metadata_can_be_updated(): void
    {
        $eventType = EventType::query()->create([
            'name' => 'Torneo',
            'slug' => 'torneo',
            'is_active' => true,
        ]);

        $event = Event::query()->create([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $eventType->id,
            'title' => 'Torneo inicial',
            'description' => 'Evento de prueba',
            'metadata' => [
                'teams' => 8,
            ],
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]);

        $response = $this->putJson("/api/events/{$event->id}", [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'metadata' => [
                'teams' => 16,
                'rules' => 'single-elimination',
            ],
        ]);

        $response->assertOk()
            ->assertJsonPath('data.metadata.teams', 16)
            ->assertJsonPath('data.metadata.rules', 'single-elimination');
    }
}
