<?php

namespace App\Services;

use App\Models\Event;
use App\Models\EventType;
use App\Repositories\EventRepository;
use Carbon\CarbonImmutable;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Arr;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Throwable;

class EventImportExportService
{
    public function __construct(
        private readonly EventService $events,
        private readonly EventRepository $eventRepository,
    ) {}

    public function import(string $appId, string $userauthId, string $format, string $path): array
    {
        $rows = $format === 'csv'
            ? $this->parseCsv($path)
            : $this->parseIcs($path);

        $created = [];
        $errors = [];

        foreach ($rows as $index => $row) {
            try {
                $event = $this->events->create($this->normalizeImportRow($row, $appId, $userauthId));
                $created[] = $this->serializeCreatedEvent($event);
            } catch (Throwable $exception) {
                $errors[] = [
                    'row' => $index + 1,
                    'message' => $this->importErrorMessage($exception),
                    'payload' => Arr::only($row, ['title', 'event_type_slug', 'start_time', 'end_time']),
                ];
            }
        }

        return [
            'created_count' => count($created),
            'failed_count' => count($errors),
            'created' => $created,
            'errors' => $errors,
        ];
    }

    public function export(array $filters): StreamedResponse
    {
        $events = $this->eventRepository->getFilteredForTenant(
            $filters['app_id'],
            $filters['userauth_id'],
            $filters,
        );

        return $filters['format'] === 'csv'
            ? $this->exportCsv($events)
            : $this->exportIcs($events);
    }

    private function parseCsv(string $path): array
    {
        $handle = fopen($path, 'r');

        if ($handle === false) {
            throw ValidationException::withMessages(['file' => ['No se pudo leer el archivo CSV.']]);
        }

        $headers = fgetcsv($handle);
        $rows = [];

        while (($values = fgetcsv($handle)) !== false) {
            $rows[] = array_combine($headers ?: [], array_pad($values, count($headers ?: []), null)) ?: [];
        }

        fclose($handle);

        return $rows;
    }

    private function parseIcs(string $path): array
    {
        $content = file_get_contents($path);

        if ($content === false) {
            throw ValidationException::withMessages(['file' => ['No se pudo leer el archivo ICS.']]);
        }

        $events = [];
        $current = null;

        foreach ($this->unfoldIcsLines($content) as $line) {
            if ($line === 'BEGIN:VEVENT') {
                $current = [];

                continue;
            }

            if ($line === 'END:VEVENT') {
                if ($current !== null) {
                    $events[] = [
                        'title' => $current['SUMMARY'] ?? null,
                        'description' => $current['DESCRIPTION'] ?? null,
                        'event_type_slug' => $current['X-EVENT-TYPE'] ?? null,
                        'start_time' => $current['DTSTART'] ?? null,
                        'end_time' => $current['DTEND'] ?? null,
                    ];
                }

                $current = null;

                continue;
            }

            if ($current === null || ! str_contains($line, ':')) {
                continue;
            }

            [$property, $value] = explode(':', $line, 2);
            $property = Str::before($property, ';');
            $current[$property] = $this->unescapeIcsText($value);
        }

        return $events;
    }

    private function normalizeImportRow(array $row, string $appId, string $userauthId): array
    {
        $eventType = EventType::query()
            ->where('slug', trim((string) ($row['event_type_slug'] ?? '')))
            ->first();

        if ($eventType === null) {
            throw ValidationException::withMessages([
                'event_type_slug' => ['El tipo de evento no existe o no fue enviado.'],
            ]);
        }

        return [
            'app_id' => $appId,
            'userauth_id' => $userauthId,
            'event_type_id' => $eventType->id,
            'title' => trim((string) ($row['title'] ?? '')),
            'description' => $row['description'] ?? null,
            'start_time' => $this->parseImportDate((string) ($row['start_time'] ?? '')),
            'end_time' => $this->parseImportDate((string) ($row['end_time'] ?? '')),
        ];
    }

    private function parseImportDate(string $value): string
    {
        $value = trim($value);

        if (preg_match('/^\d{8}T\d{6}Z$/', $value) === 1) {
            return CarbonImmutable::createFromFormat('Ymd\THis\Z', $value, 'UTC')->toDateTimeString();
        }

        if (preg_match('/^\d{8}T\d{6}$/', $value) === 1) {
            return CarbonImmutable::createFromFormat('Ymd\THis', $value)->toDateTimeString();
        }

        return CarbonImmutable::parse($value)->toDateTimeString();
    }

    private function exportCsv(Collection $events): StreamedResponse
    {
        return response()->streamDownload(function () use ($events): void {
            $handle = fopen('php://output', 'w');
            fputcsv($handle, ['title', 'description', 'event_type_slug', 'start_time', 'end_time']);

            $events->each(function (Event $event) use ($handle): void {
                fputcsv($handle, [
                    $event->title,
                    $event->description,
                    $event->eventType?->slug,
                    $event->start_time?->toISOString(),
                    $event->end_time?->toISOString(),
                ]);
            });

            fclose($handle);
        }, 'events.csv', ['Content-Type' => 'text/csv']);
    }

    private function exportIcs(Collection $events): StreamedResponse
    {
        return response()->streamDownload(function () use ($events): void {
            echo "BEGIN:VCALENDAR\r\n";
            echo "VERSION:2.0\r\n";
            echo "PRODID:-//TusSalonesEventos//Events//ES\r\n";

            $events->each(function (Event $event): void {
                echo "BEGIN:VEVENT\r\n";
                echo 'UID:event-'.$event->id."@tussaloneseventos\r\n";
                echo 'SUMMARY:'.$this->escapeIcsText($event->title)."\r\n";
                echo 'DESCRIPTION:'.$this->escapeIcsText((string) $event->description)."\r\n";
                echo 'DTSTART:'.$this->formatIcsDate($event->start_time)."\r\n";
                echo 'DTEND:'.$this->formatIcsDate($event->end_time)."\r\n";
                echo 'X-EVENT-TYPE:'.$this->escapeIcsText((string) $event->eventType?->slug)."\r\n";
                echo "END:VEVENT\r\n";
            });

            echo "END:VCALENDAR\r\n";
        }, 'events.ics', ['Content-Type' => 'text/calendar']);
    }

    private function serializeCreatedEvent(Event $event): array
    {
        return [
            'id' => $event->id,
            'title' => $event->title,
            'event_type_slug' => $event->eventType?->slug,
            'start_time' => $event->start_time?->toISOString(),
            'end_time' => $event->end_time?->toISOString(),
        ];
    }

    private function importErrorMessage(Throwable $exception): string
    {
        if ($exception instanceof ValidationException) {
            return collect($exception->errors())->flatten()->implode(' ');
        }

        return $exception->getMessage();
    }

    private function unfoldIcsLines(string $content): array
    {
        $lines = preg_split('/\r\n|\n|\r/', $content) ?: [];
        $unfolded = [];

        foreach ($lines as $line) {
            if (($line[0] ?? '') === ' ' || ($line[0] ?? '') === "\t") {
                $unfolded[array_key_last($unfolded)] .= substr($line, 1);

                continue;
            }

            $unfolded[] = $line;
        }

        return $unfolded;
    }

    private function escapeIcsText(string $value): string
    {
        return str_replace(['\\', ';', ',', "\r\n", "\n", "\r"], ['\\\\', '\;', '\,', '\n', '\n', '\n'], $value);
    }

    private function unescapeIcsText(string $value): string
    {
        return str_replace(['\n', '\,', '\;', '\\\\'], ["\n", ',', ';', '\\'], $value);
    }

    private function formatIcsDate(mixed $value): string
    {
        return CarbonImmutable::parse($value)->utc()->format('Ymd\THis\Z');
    }
}
