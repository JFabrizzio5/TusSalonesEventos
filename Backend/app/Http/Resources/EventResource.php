<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EventResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'app_id' => $this->app_id,
            'userauth_id' => $this->userauth_id,
            'event_type_id' => $this->event_type_id,
            'event_type' => $this->whenLoaded('eventType', fn () => [
                'id' => $this->eventType->id,
                'name' => $this->eventType->name,
                'slug' => $this->eventType->slug,
            ]),
            'title' => $this->title,
            'description' => $this->description,
            'metadata' => $this->metadata,
            'start_time' => $this->start_time?->toISOString(),
            'end_time' => $this->end_time?->toISOString(),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}
