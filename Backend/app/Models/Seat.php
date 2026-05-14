<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Seat extends Model
{
    //Proteccion contra asignacion masiva

    //Realcion muchos a uno (zonas-asientos)
    public function zone()
    {
        return $this->belongsTo(Zone::class);
    }
}
