<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Event extends Model
{
    protected $fillable = [
        'title',
        'description',
        'metadata',
        'start_time',
        'end_time',
        'event_type_id',
        'app_id',
        'userauth_id',
    ];

    protected function casts(): array
    {
        return [
            'metadata' => 'array',
            'start_time' => 'datetime',
            'end_time' => 'datetime',
        ];
    }

    public function eventType(): BelongsTo
    {
        return $this->belongsTo(EventType::class);
    }

    public function scopeForTenant(Builder $query, string $appId, string $userAuthId): Builder
    {
        return $query->where('app_id', $appId)
            ->where('userauth_id', $userAuthId);
    }
}
