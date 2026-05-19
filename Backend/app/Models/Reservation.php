<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Reservation extends Model
{
    protected $fillable = [
        'ticket_id',
        'userauth_id',
        'guest_count',
        'status'
    ];

    protected $casts = [
        'guest_count' => 'integer',
        'created_at' => 'datetime:Y-m-d H:i:s',
        'updated_at' => 'datetime:Y-m-d H:i:s',
    ];

    /**
     * Relación:
     * Una reservación pertenece a un ticket
     */
    public function ticket()
    {
        return $this->belongsTo(Ticket::class);
    }
}