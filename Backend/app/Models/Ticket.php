<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Ticket extends Model
{
    //Protected filled
    protected $fillable = [
        'event_id',
        'seat_id',
        'price'
    ];

    //Casting de tipos de datos
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s',
        'updated_at' => 'datetime:Y-m-d H:i:s',
    ];
    
    //Relaciónes con un evento a un asiento
    public function event()
    {
        return $this->belongsTo(Event::class);
    }

    //Relaciónes con un asiento a un ticket
    public function seat()
    {
        return $this->belongsTo(Seat::class);
    }
}
