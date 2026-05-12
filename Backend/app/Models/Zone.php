<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Zone extends Model
{
    //Protected $fillable 
    protected $fillable = [
        'salon_id',
        'name'
    ];

    //Relacion muchos a uno(salones-zonas)
    public function salon()
    {
        $this -> belongsTo(Salon::class);
    }
}
