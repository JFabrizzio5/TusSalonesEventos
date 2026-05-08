<?php

namespace Tests\Feature;

use App\Models\Event;
use App\Models\EventType;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Tests\TestCase;

class EventImportExportTest extends TestCase
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

    public function test_it_imports_valid_csv_events(): void
    {
        $response = $this->post('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'csv',
            'file' => UploadedFile::fake()->createWithContent('events.csv', implode("\n", [
                'title,description,event_type_slug,start_time,end_time',
                'Evento CSV,Descripcion,cine,2026-06-01 10:00:00,2026-06-01 12:00:00',
            ])),
        ]);

        $response->assertOk()
            ->assertJsonPath('created_count', 1)
            ->assertJsonPath('failed_count', 0)
            ->assertJsonPath('created.0.title', 'Evento CSV');

        $this->assertDatabaseHas('events', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'title' => 'Evento CSV',
        ]);
    }

    public function test_it_partially_rejects_invalid_csv_rows(): void
    {
        $response = $this->post('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'csv',
            'file' => UploadedFile::fake()->createWithContent('events.csv', implode("\n", [
                'title,description,event_type_slug,start_time,end_time',
                'Evento valido,Descripcion,cine,2026-06-01 10:00:00,2026-06-01 12:00:00',
                'Evento invalido,Descripcion,,2026-06-02 10:00:00,2026-06-02 12:00:00',
            ])),
        ]);

        $response->assertOk()
            ->assertJsonPath('created_count', 1)
            ->assertJsonPath('failed_count', 1)
            ->assertJsonPath('errors.0.row', 2);
    }

    public function test_it_rejects_imported_events_with_schedule_conflicts(): void
    {
        Event::query()->create($this->eventPayload([
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ]));

        $response = $this->post('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'csv',
            'file' => UploadedFile::fake()->createWithContent('events.csv', implode("\n", [
                'title,description,event_type_slug,start_time,end_time',
                'Evento conflicto,Descripcion,cine,2026-06-01 11:00:00,2026-06-01 13:00:00',
            ])),
        ]);

        $response->assertOk()
            ->assertJsonPath('created_count', 0)
            ->assertJsonPath('failed_count', 1);
    }

    public function test_it_imports_valid_ics_events(): void
    {
        $response = $this->post('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'ics',
            'file' => UploadedFile::fake()->createWithContent('events.ics', implode("\r\n", [
                'BEGIN:VCALENDAR',
                'VERSION:2.0',
                'BEGIN:VEVENT',
                'SUMMARY:Evento ICS',
                'DESCRIPTION:Descripcion ICS',
                'DTSTART:20260602T100000Z',
                'DTEND:20260602T120000Z',
                'X-EVENT-TYPE:cine',
                'END:VEVENT',
                'END:VCALENDAR',
            ])),
        ]);

        $response->assertOk()
            ->assertJsonPath('created_count', 1)
            ->assertJsonPath('failed_count', 0)
            ->assertJsonPath('created.0.title', 'Evento ICS');
    }

    public function test_it_rejects_ics_events_without_event_type(): void
    {
        $response = $this->post('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'ics',
            'file' => UploadedFile::fake()->createWithContent('events.ics', implode("\r\n", [
                'BEGIN:VCALENDAR',
                'BEGIN:VEVENT',
                'SUMMARY:Evento sin tipo',
                'DTSTART:20260602T100000Z',
                'DTEND:20260602T120000Z',
                'END:VEVENT',
                'END:VCALENDAR',
            ])),
        ]);

        $response->assertOk()
            ->assertJsonPath('created_count', 0)
            ->assertJsonPath('failed_count', 1);
    }

    public function test_it_exports_csv_filtered_by_tenant(): void
    {
        Event::query()->create($this->eventPayload(['title' => 'Evento exportable']));
        Event::query()->create($this->eventPayload([
            'app_id' => 'app-b',
            'title' => 'Evento externo',
        ]));

        $response = $this->get('/api/events/export?app_id=app-a&userauth_id=user-a&format=csv');
        $content = $response->streamedContent();

        $response->assertOk();
        $this->assertStringContainsString('Evento exportable', $content);
        $this->assertStringNotContainsString('Evento externo', $content);
    }

    public function test_it_exports_ics_filtered_by_tenant(): void
    {
        Event::query()->create($this->eventPayload(['title' => 'Evento ICS exportable']));
        Event::query()->create($this->eventPayload([
            'userauth_id' => 'user-b',
            'title' => 'Evento externo ICS',
        ]));

        $response = $this->get('/api/events/export?app_id=app-a&userauth_id=user-a&format=ics');
        $content = $response->streamedContent();

        $response->assertOk();
        $this->assertStringContainsString('BEGIN:VCALENDAR', $content);
        $this->assertStringContainsString('SUMMARY:Evento ICS exportable', $content);
        $this->assertStringNotContainsString('Evento externo ICS', $content);
    }

    public function test_it_validates_import_format_and_file(): void
    {
        $this->postJson('/api/events/import', [
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'format' => 'xlsx',
        ])->assertUnprocessable()
            ->assertJsonValidationErrors(['format', 'file']);
    }

    private function eventPayload(array $overrides = []): array
    {
        return array_merge([
            'app_id' => 'app-a',
            'userauth_id' => 'user-a',
            'event_type_id' => $this->cineType->id,
            'title' => 'Evento exportado',
            'description' => 'Evento de prueba',
            'start_time' => '2026-06-01 10:00:00',
            'end_time' => '2026-06-01 12:00:00',
        ], $overrides);
    }
}
