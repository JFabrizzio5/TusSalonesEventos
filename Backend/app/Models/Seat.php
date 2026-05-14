<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Seat extends Model
{
    //Proteccion contra asignacion masiva
    protected $fillable = [
        'zone_id',
        'row',
        'number'
    ];
    //Casting de dates
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s',
        'updated_at' => 'datetime:Y-m-d H:i:s',
    ];
    //Realcion muchos a uno (zonas-asientos)
    public function zone()
    {
        return $this->belongsTo(Zone::class);
    }
}
